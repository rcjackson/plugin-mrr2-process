import serial
import time
import argparse
import xarray as xr
import tempfile
import subprocess
import threading
import glob
import os
import shutil
import sage_data_client
import requests

from waggle.plugin import Plugin
from datetime import datetime, timezone, timedelta


def parse_mrr_signal(serial, plugin):
    """
    This parses the incoming signal from the MRR and writes the data to a file for
    processing by IMProToo.

    Parameters
    ----------
    serial: PySerial serial connection
        The serial connection to pull from.
    plugin: Plugin instance
        The plugin instance.
    out_file: file handle
        The output file handle to write to.
    """
    # Hex 01 is the start of an MRR record
    # Hex 02 is the start of a raw spectra line
    # Beginning of record, need to add the UTC date and time and MRR
    record_started = False
    exit = False
    out_file = None
    while exit == False:
        try:
            line = serial.readline()
        except:
            continue
        if line.startswith(b'\x01'):
            cur_time = datetime.now(timezone.utc)
            time_str = datetime.strftime(cur_time, "%y%m%d%H%M%S")
            if out_file is None:
                out_file_name = '%s.raw' % time_str
                out_file = open(out_file_name, 'w')
            out_line = "MRR %s UTC " % time_str + line[2:-5].decode("utf-8") + "\n"
            out_file.write(out_line)
            record_started = True
            print("Start MRR record %s" % time_str)
        # Line in middle of record    
        if line.startswith(b'\x02') and record_started:
            out_file.write(line[1:-5].decode("utf-8") + "\n")
        # End of record, if we have record written then close.
        if line.startswith(b'\x04'):
            if record_started:
            # Write new record every 5 minutes    
                if cur_time.minute == 0 and cur_time.second < 10:
                    out_file.close()
                    out_file = None
                    print(out_file_name)
                    plugin.upload_file(out_file_name, keep=True)
                    shutil.move(out_file_name, '/app/raw_files/' + out_file_name)
                    exit = True

def readtofile(uurl, ff):
    r = requests.get(uurl)
    if r.status_code == 200:
        print('Downloading %s' % uurl[-14:])
        with open(ff, 'wb') as out:
            for bits in r.iter_content():
                out.write(bits)
    
    return True

def process_hour(args):
    cur_time = datetime.now()
    previous_hour = cur_time - timedelta(hours=1)
    df = sage_data_client.query(
            start="-%dh" % args.process,
            filter={"vsn": "W057", "name": "upload", "task": "mrr2",
                    }).set_index("timestamp")
    if not os.path.exists('/app/raw_files/'):
        os.makedirs('/app/raw_files/')
    file_list = df['value'].values
    for f in file_list:
        last_file = None
        if '.raw' in f:
            last_file = f
        if last_file is None:
            continue
        out_name = os.path.join('/app/raw_files', last_file[-16:])
        readtofile(last_file, out_name)
        year = '20' + last_file[-16:-14]
        month = last_file[-14:-12]
        day = last_file[-12:-10]
        hour = last_file[-10:-8]
        date_str = '%s%s%s.%s0000' % (year, month, day, hour)
        fname_str = 'mrr2atmos.%s.nc' % date_str
        subprocess.run(["python3", "RaProM_38.py", fname_str])
        with Plugin() as plugin:
            plugin.upload_file('/app/raw_files/' + fname_str)
        os.remove(out_name)
    print("Published %s" % fname_str)


def main(args):
    if not os.path.exists('/app/raw_files/'):
        os.makedirs('/app/raw_files/')
    with serial.Serial(
            args.device, 57600, parity=serial.PARITY_NONE,
            xonxoff=True, timeout=args.timeout) as ser:
        print("Serial connection to %s open" % args.device)
        with Plugin() as plugin:
            while True:    
                parse_mrr_signal(ser, plugin)
                


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Plugin for transferring the MRR-2 data.")
    parser.add_argument("--device",
            type=str,
            dest='device',
            default='/dev/ttyUSB1',
            help='serial device to use')
    parser.add_argument("--timeout",
            type=float,
            dest='timeout',
            default=1,
            help="Number of seconds before signal timeout.")
    parser.add_argument("--process",
            type=int,
            default=0,
            help="Number of files to process (0 for retrieve mode)",
            dest='process')


    args = parser.parse_args()
    if args.process == 0:
        main(args)
    else:
        process_hour(args)
