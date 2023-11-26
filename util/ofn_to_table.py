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
    match = re.search(r'\<.+?\>', text)
    if match:
        return match.group()[1:-1]
    else:
        match = re.search(r'\:\w+\-', text)

        if match:
            return match.group()[1:]
        else:
            return None


def make_buffer_dict(file_name:str) -> dict:
    buffer = {}
    with open(file_name) as f:
        for idx, line in enumerate(f.readlines()):
            if line.startswith("Declaration(") and check_line(line):
                iri = parse_iri(line)
                buffer[iri] = []

    return buffer

def main(file_name:str="test.ofn"):
    buffer = make_buffer_dict(file_name) # seed dict with IRIs
    iri = ""

    with open(file_name) as f:
        for idx, line in enumerate(f.readlines()):
            line = line.strip()
            
            if line.startswith("# Object Property:") or line.startswith("# Class:"):
                # print(line)
                iri = parse_iri(line)
                # iri = idxs
            elif check_line(line) and len(iri) > 0 and buffer.get(iri) is not None:
                # print('line', line)
                # print(iri, ':', line)

                buffer[iri].append(line)

            # print('buffer', buffer.get(iri))
    # pd.set_option('display.max_colwidth', None)
    pd.options.display.max_colwidth = 30
    df = pd.DataFrame.from_dict(buffer, orient='index')
    df = df.fillna("")
    # df = pd.DataFrame({ key:pd.Series(value) for key, value in buffer.items() })
    # df.columns = ['ofn']
    # print('cols', df.columns)
    # print(df)
    # print('------')
    df_combined = pd.DataFrame(data=df.apply(lambda row: '_'.join(row.values.astype(str)), axis=1), columns=['combined'])
    df_combined['combined_length'] = df_combined['combined'].apply(len)
    # print(df_combined)
    # print('------')
    df_melt = df.melt(ignore_index=False).drop(columns='variable')
    df_melt['value_length'] = df_melt['value'].apply(len)
    # print(df_melt)

    # pprint(buffer)
    return df.sort_index(), df_combined.sort_index(), df_melt.sort_index()

if __name__ == '__main__':
    df, df_combined, df_melt = main()
    print(df_melt)

