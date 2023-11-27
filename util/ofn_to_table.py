#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import re
import pandas as pd
from pprint import pprint


def check_line(line:str) -> bool:
    return (
        len(line) > 0 
        and not line.startswith('#')
        and not line.startswith(')')
        and "http://purl.org/dc/terms/created" not in line
        and "http://www.geneontology.org/formats/oboInOwl#creation_date" not in line
        and "http://purl.org/dc/elements/1.1/contributor" not in line
        and "http://purl.org/dc/terms/contributor" not in line
    )


def parse_iri(text:str) -> str:
    # search for iri between <>, this includes https://...
    match = re.search(r'\<.+?\>', text)
    if match:
        return match.group()[1:-1] # dont't return closing ">"
    else:
        # serch curie
        match = re.search(r'\:\w+\-', text)

        if match:
            return match.group()[1:] # return text after the ":"
        else:
            return None


def make_buffer_dict(file:str) -> dict:
    buffer = {}
    with open(file) as f:
        for idx, line in enumerate(f.readlines()):
            # create a dict for declared entities
            if line.startswith("Declaration(") and check_line(line):
                iri = parse_iri(line)
                buffer[iri] = []

    return buffer


def ofn_to_df(file:str):
    buffer = make_buffer_dict(file) # seed dict with IRIs
    iri = ""

    # reading the file creates list of axioms for each IRI key in the buffer dict
    with open(file) as f:
        for idx, line in enumerate(f.readlines()):
            line = line.strip()
            
            # parse IRI out of commented line
            if (
                line.startswith("# Object Property:") 
                or line.startswith("# Class:")
                or line.startswith("# Data Property")
                or line.startswith("# Individual")
            ):
                iri = parse_iri(line)
            
            # append axiom to list associated with IRI key
            elif check_line(line) and len(iri) > 0 and buffer.get(iri) is not None:
                buffer[iri].append(line)
    
    df = pd.DataFrame(
        {
            'iri': list(buffer.keys()),
            'axiom': list(buffer.values())
         }
    )
    df = df.explode('axiom').reset_index(drop=True) # explode axiom list
    return df
    

@click.command
@click.option("--file", "-f")
def main(file:str):
    df = ofn_to_df(file)
    return print(df)


if __name__ == '__main__':
    main()

