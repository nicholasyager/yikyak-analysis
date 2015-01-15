#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(description="Fix an improper csv.")
parser.add_argument('path',metavar='path')

args = parser.parse_args()

print(args.path)

outputFile = open(args.path[:-4] +"_fixed.csv","w")

with open(args.path, "r") as f:
    for line in f:
        line = line.rstrip()
        columns = line.split(",")
        fixedColumns = []
        for column in columns:
            if column[0] != '"':
                column = '"'+column
            elif column[-1] != '"':
                columns = column + '"'
            fixedColumns.append(column)
        outputFile.write(','.join(fixedColumns)+"\n")
