# Name:         duplicate_unique_id_alert
# Purpose:      sends email alert when duplicate unique ID records are found
# Author:       pfautz
# Created:      10/12/2017
# Modified:
# Requirements: the items in the fcs,field,and to_email lists must be in the same
#               order (e.g. road_centerline is first in fcs, STSEGID is first in
#               field, and the proper recipient is first in to_emails.
# ------------------------------------------------------------------------------

# Import Modules
import arcpy
import csv
import logging
from logging import handlers
import sys
import traceback
import os
# ------------------------------------------------------------------------------

# Local Variables
sde = r"\\path\to\SDE.sde"
fcs = [sde+"\path\to\fc1",
        sde+"\path\to\fc2",
        sde+"\path\to\fc3"]
field = ["field1","field2","field3"]
to_emails = ["email1","email2","email3"]
# ------------------------------------------------------------------------------

# Logging
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

# .log Error
fh1 = logging.FileHandler(r"\\path\to\log\folder"+"\\duplicate_unique_id_alert.log")
fh1.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                                    datefmt='%Y-%m-%d %H:%M:%S')
fh1.setFormatter(formatter)
my_logger.addHandler(fh1)

# Email Error
smtp_handler1 = logging.handlers.SMTPHandler(mailhost=("webserver", 25),
                                            fromaddr="from_email",
                                            toaddrs="to_email",
                                            subject=u"duplicate_unique_id_alert failed")
smtp_handler1.setLevel(logging.ERROR)
my_logger.addHandler(smtp_handler1)
# ------------------------------------------------------------------------------

# Function
def duplicate_unique_id(fcs,field,to_emails):
    try:
        for fc in fcs:
            # Get file basename
            describe=arcpy.Describe(fc)
            basename=describe.baseName
            basename = basename.split(".")[-1]
            print basename

            # Get field name
            field1 = field[fcs.index(fc)]
            print field1
            # --------------------------------------------------------------------------

            # .log Error
            fh = logging.FileHandler(r"\\path\to\log\folder"+"\\"+basename+field1+"_duplicate_unique_id.log")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            my_logger.addHandler(fh)

            # Email Error
            smtp_handler = logging.handlers.SMTPHandler(mailhost=("webserver", 25),
                                                        fromaddr="from_email",
                                                        toaddrs=str(to_emails[fcs.index(fc)]),
                                                        subject=u"Duplicates found in SDE "+basename+" "+field1)
            smtp_handler.setLevel(logging.INFO)
            my_logger.addHandler(smtp_handler)
            # --------------------------------------------------------------------------

            # List of all field values including duplicates
            with arcpy.da.SearchCursor(fc,field1) as sCursor1:
                list1=[]
                for row in sCursor1:
                    list1.append(row[0])
            print "records",len(list1)
            # --------------------------------------------------------------------------

            # Isolate duplicates from list
            unique_set=set()
            duplicates=[]
            for value in list1:
                if value not in unique_set:
                    unique_set.add(value)
                elif value in unique_set:
                    duplicates.append(value)
            print "before",len(duplicates)
            duplicates_set=set(duplicates)
            print "after",len(duplicates_set)
            # --------------------------------------------------------------------------

            # Count instances of each dup
            list_counts=[]
            if len(duplicates_set)!=0:
                for dup in duplicates_set:
                    dup_instances=duplicates.count(dup)
                    list2=[dup,dup_instances+1]
                    list_counts.append(list2)
                print list_counts

                # Save to csv
                csvfile = r"\\output\csv\folder"+"\\"+basename+field1+"_dups"+".csv"
                with open(csvfile, "w") as output:
                    writer = csv.writer(output,lineterminator='\n')
                    writer.writerow([field1,"Count"])
                    writer.writerows(list_counts)
                my_logger.info("Duplicates found in SDE "+basename+"\n"+".csv can be found here: "+csvfile)
            else:
                my_logger.debug("No duplicates found in SDE "+basename)
                try:
                    os.remove(r"\\output\csv\folder"+"\\"+basename+field1+"_dups"+".csv")
                except OSError:
                    pass
            # --------------------------------------------------------------------------

            # Remove handlers
            my_logger.removeHandler(fh)
            my_logger.removeHandler(smtp_handler)

    except arcpy.ExecuteError:
        my_logger.error("ArcPy ExecuteError:\n" + arcpy.GetMessages(2) + "\n")

    except Exception as e:
        # Capture the original error
        error = "ERROR: " + str(e) + "\n"

        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        my_logger.error(error + "\n" + pymsg + "\n\n" + msgs)
    # --------------------------------------------------------------------------

# Run
duplicate_unique_id(fcs,field,to_emails)