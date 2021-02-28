#!/bin/bash
#
# Check for empty arguments. We need a text file as input
#
if [ -z "$1" ] ; then
    printf "\nusage: %s <GDPdU_export_file>%s\n\n" $(basename $0)
    exit 1
fi

file=$1
bText="Korrekturbuchung"

# we use a shell array for the periods we want to analyze

arrVar=()

# add search patterns as shell array elements

arrVar+=("2018-01-01 2018-02-01")
arrVar+=("2018-02-01 2018-03-01")
arrVar+=("2018-03-01 2018-04-01")
arrVar+=("2018-04-01 2018-05-01")
arrVar+=("2018-05-01 2018-06-01")
arrVar+=("2018-06-01 2018-07-01")
arrVar+=("2018-07-01 2018-08-01")
arrVar+=("2018-08-01 2018-09-01")
arrVar+=("2018-09-01 2018-10-01")
arrVar+=("2018-10-01 2018-11-01")
arrVar+=("2018-11-01 2018-12-01")
arrVar+=("2018-12-01 2019-01-01")

# Iterate the loop to execute each run

for period in "${arrVar[@]}"
do
  printf "\n#### GDPdU Analyse Periode ist %s %s\n\n" $period
  analyzeGDPdU.py -f "${file}" -p $period -t $bText
done

# Combine the output files into one

# analyzeGDPdU.py version 1.15.1 will create
# collective posting output file names
# according to the following naming convention
# ${file%.*}_Sammelbuchungen_vom_2018-01-01_bis_2018-02-01
# We expect one file per period (12 requested)

cpoutbase=${file%.*}
cpoutbase+="_Sammelbuchungen_vom_2018"

# We need a list of all ollective posting output files.
# One robust way in bash is to expand into an array,

pattern="${cpoutbase}-*"
sbfiles=( $pattern )

# the name of the combined monthly output file

outfile=${file%.*}
outfile+="_Sammelbuchungen_2018_monatlich.csv"

# We use the header from the first element
# (headers are all the same)
# and then add all files without header
# tail -n +2 is required to skip the first line on macOS
# tail -q suppresses the printout of filenames

printf "\n#### Concatenating collective postings to %s\n\n" $outfile

head -1 "${sbfiles[0]}" > "${outfile}"
tail -n +2 -q "${sbfiles[@]}" >> "${outfile}"
