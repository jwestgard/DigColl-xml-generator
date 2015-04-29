#!/usr/bin/env python3

import sys, subprocess

required_columns =[ "Accession", "AlternateTitle", "ArchivalCollection", "AspectRatio",
                    "Box", "Century", "Color", "Continent", "Contributor", 
                    "ContributorType", "CopyrightHolder", "CorpScheme", "CorpSubject", 
                    "Country", "Creator", "CreatorType", "DataRate", "DateAttribute", 
                    "DateCreated", "DateDigitized", "Department", "Description/Summary", 
                    "DigitizationNotes", "DigitizedByDept", "DigitizedByPers", 
                    "Dimensions", "DurationDerivatives", "FileName", "Form", "Format", 
                    "FormType", "FrameRate", "GeographicalScheme", "GeographicalSubject", 
                    "HorizontalPixels", "Identifier", "Item", "Language", "MediaType", 
                    "Mono/Stereo", "PersonalScheme", "PersonalSubject", 
                    "Provider/Publisher", "Provider/PublisherType", "Region/State", 
                    "RepositoryBrowse", "Rights", "ScanSignal", "Series", 
                    "Settlement/City", "SharestreamURLs", "Subseries", "Title", 
                    "TopicalScheme", "TopicalSubject", "TrackFormat", "VerticalPixels", 
                    "VideoStandard", "XMLType" ]

bashCommand = "in2csv {0}".format(sys.argv[1])

bashout = subprocess.check_output(bashCommand.split())

firstline = bashout.decode('utf-8').split('\n')[0]

columns_to_check = sorted(firstline.split(','))

for c in required_columns:
    if c in columns_to_check:
        print("Found {0}!".format(c))
    else:
        print("--> ERROR: {0} not found!".format(c))
    
