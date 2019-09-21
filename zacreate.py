#!/usr/bin/env python

# IFDY:USE:any

import argparse
import os
import re
import datetime
import logging
import sys
import codecs

PIDGIN_LOG_DIR = os.path.join( os.path.expanduser( '~' ), '.purple', 'logs' )
ERROR_NO_ARCHIVE = 1

def archive_create( archive_path, key, salt=None, item_list=[], index=True ):

    ''' Item list must be in the format:
    [{'path_rel, 'contents'}] '''

    # TODO: Add archive_current status update stuff.

    logger = logging.getLogger( 'archive.create' )

    # Generate the salt if applicable.
    if not salt:
        salt = Random.get_random_bytes( 160 )
        logger.debug( 'Salt generated: {}'.format(
            base64.b64encode( salt )
        ) )

    if index:
        # Create the search index for the archive.
        schema = whoosh.fields.Schema(
            path=whoosh.fields.ID(stored=True),
            content=whoosh.fields.TEXT
        )
        ix_storage = whoosh.filedb.filestore.RamStorage()
        ix = ix_storage.create_index( schema )
        ix_writer = ix.writer()
    
    # Read all of the logs and write them to the archive ZIP.
    arcio = StringIO.StringIO()
    total_bytes = 0
    with zipfile.ZipFile( arcio, 'w', zipfile.ZIP_DEFLATED ) as arcz:
        for item in item_list:
            # Make sure everything is in unicode, first.
            if isinstance( item['path_rel'], str ):
                item['path_rel'] = item['path_rel'].decode( 'ascii' )
            if isinstance( item['contents'], str ):
                item['contents'] = item['contents'].decode( 'ascii' )

            # Replace special characters with entities.
            item['path_rel'] = \
                item['path_rel'].encode( 'ascii', errors='xmlcharrefreplace' )
            item['path_rel'] = item['path_rel'].decode( 'ascii' )
            item['contents'] = \
                item['contents'].encode( 'ascii', errors='xmlcharrefreplace' )
            item['contents'] = item['contents'].decode( 'ascii' )

            # Index the item if applicable.
            if index:
                logger.info( 'Indexing {}...'.format( item['path_rel'] ) )
                ix_writer.add_document(
                    path=item['path_rel'][1:],
                    content=item['contents']
                )

            # Store the item.
            logger.info( 'Storing {}...'.format( item['path_rel'] ) )
            arcz.writestr(
                item['path_rel'].decode( 'ascii' ),
                item['contents'].decode( 'ascii' )
            )
            total_bytes += len( item['contents'] )

        if index:
            # Write the search index to the ZIP.
            ix_writer.commit()
            for ix_file_name in ix_storage.list():
                with ix_storage.open_file( ix_file_name ) as ix_file:
                    logger.info( 'Storing {}...'.format( ix_file_name ) )
                    ix_contents = ix_file.read()
                    arcz.writestr(
                        os.path.join( '/index', ix_file_name ),
                        ix_contents
                    )
                    total_bytes += len( ix_contents )

    logger.info( 'Stored {} bytes.'.format( total_bytes ) )

    # Setup the encryptor. Expand and set the key.
    iv = Random.get_random_bytes( 16 )
    key_crypt = pbkdf2.PBKDF2( key, salt ).read( 32 )
    encryptor = AES.new( key_crypt, AES.MODE_CBC, iv )

    # Open the output file and start writing.
    arcio.seek( 0, os.SEEK_SET )
    with open( archive_path, 'wb' ) as archive_file:
        archive_file.write( VERSIONS[len( VERSIONS ) - 1] )
        archive_file.write( salt )
        archive_file.write( struct.pack( '<Q', len( arcio.getvalue() ) ) )
        archive_file.write( iv )
        # Process each chunk of the ZIP.
        while True:
            chunk = arcio.read( CHUNK_LEN )
            if len( chunk ) == 0:
                # We're done!
                break
            elif 0 != len( chunk ) % 16:
                # Handle the trailing end.
                chunk += ' ' * (16 - len( chunk ) % 16)
            archive_file.write( encryptor.encrypt( chunk ) )

def list_logs(
    protocols_accounts, date_start=None, date_end=None, log_dir=PIDGIN_LOG_DIR
):

    ''' Build and return a list of all logs between the specified dates. 
    protocols_accounts should be in the format of {'protocol': ['account']}. '''

    logger = logging.getLogger( 'archive.pidginlogs.list' )

    list_out = []

    # Fill in missing parameters.
    if not date_start:
        date_start = datetime.date.min
    if not date_end:
        date_end = datetime.date.today()

    # A regex to match the date format presented in the log filenames.
    re_logdate = re.compile(
        r'(?P<year>[0-9]+?)\-(?P<month>[0-9]+?)\-(?P<day>[0-9]+?)\.' +
            r'(?P<hour>[0-9].)(?P<minute>[0-9].)(?P<second>[0-9].)' +
            r'(?P<timezone>\-.+)?.txt'
    )

    if protocols_accounts:
        # TODO: A list of protocols/accounts has been specified, so walk them
        #         specifically.
        for account_list in protocols_accounts.iteritems:
            for root, dirnames, filenames in os.walk( log_dir ):
                print root
    else:
        # Walk all protocols and accounts.
        for root, dirnames, filenames in os.walk( log_dir ):
            for filename in filenames:
                fn_match = re_logdate.match( filename )
                if fn_match:
                    date_log = datetime.date(
                        int( fn_match.group( 'year' ) ),
                        int( fn_match.group( 'month' ) ),
                        int( fn_match.group( 'day' ) )
                    )
                    if date_log >= date_start and date_log <= date_end:
                        # The log is within range, so add it to the list.
                        log_path = os.path.join( root, filename )
                        try:
                            with codecs.open(
                                log_path, encoding='utf-8', mode='r'
                            ) as log_file:
                                list_out.append( {
                                    'path_abs': log_path,
                                    'path_rel': log_path[len( log_dir ):],
                                    'contents':  log_file.read()
                                } )
                        except Exception, e:
                            logger.warning(
                                'Unable to open "{}" as utf-8, attempting latin1...'
                                    .format(
                                        log_path
                                    )
                            )
                            with codecs.open(
                                log_path, encoding='latin1', mode='r'
                            ) as log_file:
                                list_out.append( {
                                    'path_abs': log_path,
                                    'path_rel': log_path[len( log_dir ):],
                                    'contents':  log_file.read()
                                } )

    return list_out

def _parse_date_arg( date_string ):
    date_match = re.match(
        # The final missing ? isn't a mistake.
        r'(?P<year>[0-9]+?)\-(?P<month>[0-9]+?)\-(?P<day>[0-9]+)',
        date_string
    )
    if None != date_match:
        return datetime.date(
            int( date_match.group( 'year' ) ),
            int( date_match.group( 'month' ) ),
            int( date_match.group( 'day' ) )
        )
    else:
        return None

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p', '--log-path', action='store', dest='log_dir', type=str,
        default=PIDGIN_LOG_DIR,
        help='The directory in which logs are contained. Defaults to {}.'.format(
            PIDGIN_LOG_DIR
        )
    )
    parser.add_argument(
        '-d', '--delete', action='store_true', dest='delete',
        help='Delete logs that are added to the archive.'
    )
    parser.add_argument(
        '-s', '--start-date', action='store', dest='start_date', default='',
        help='The date to start the archive from, in the format YYYY-MM-DD.'
    )
    parser.add_argument(
        '-e', '--end-date', action='store', dest='end_date', default='',
        help='The date to stop the archive at, in the format YYYY-MM-DD.'
    )
    parser.add_argument(
        'archive_path', action='store',
        help='The archive file to create.'
    )

    args = parser.parse_args()

    logging.basicConfig( level=logging.INFO )
    logger = logging.getLogger( 'archive.pidginlogs' )

    # Get the key from stdin.
    logger.info( 'Enter archive encryption key:' )
    key = sys.stdin.readline().strip()

    log_list = list_logs(
        {},
        _parse_date_arg( args.start_date ),
        _parse_date_arg( args.end_date ),
        args.log_dir
    )
    archive_create(
        args.archive_path,
        key,
        item_list=log_list
    )
    # Perform deletions last to make sure everything else was successful
    # first.
    if args.delete:
        for item in log_list:
            # Remove file if requested.
            os.unlink( item['path_abs'] )

            # Remove parent directories if empty.
            try:
                parent_path = os.path.dirname( item['path_abs'] )
                os.rmdir( parent_path )
                logger.info(
                    'Removed empty directory {}.'.format( parent_path )
                )
            except:
                logger.debug(
                    'Not removing non-empty directory {}.'.format( parent_path )
                )

if '__main__' == __name__:
    main()

