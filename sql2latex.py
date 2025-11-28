#!/usr/bin/env python3

# sql2latex - connects to an Oracle DB server, runs queries and generates LaTeX code from the output
# Copyright (C) 2025 Bartosz Miziała 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Contact: xmpp://arte@xmpp.tramwaj.ovh

import argparse
import oracledb
import sqlparse
from sys import stderr, exit
from pylatexenc.latexencode import unicode_to_latex
import re

DB_USER=""
DB_PASSWORD=""
DB_DSN=""
DB_LIB_DIR=""

def parse_srcipts(file_path):
    scripts = []
    with open(file_path, "r") as file:
        script = []
        for line in file:
            if line.startswith("-- Task"):
                num = int(line[8:])
                if script:
                    scripts.append((num - 1, script))
                    script = []

            script.append(line)

        scripts.append((scripts[-1][0] + 1, script))

    return scripts


def print_header(author, title):
    print(
r"""
\documentclass{article}
\usepackage{minted}
\usepackage{geometry}
\usepackage{amsmath}
\usepackage{tabularx}

\geometry{a4paper,left=1cm,right=1cm,top=2cm,bottom=2cm}
\author{AUTHOR}
\title{\vspace{-2cm} TITLE}
\date{}
""".replace("AUTHOR", author)
    .replace("TITLE", title)
    )

def sanitize_latex(string):
    string = unicode_to_latex(string, non_ascii_only=False) 
    string = string.replace("|", r"\text{\textbar}")
    string = re.sub(r" {2,}", lambda m: "~" * len(m.group(0)), string)
    return string

def print_table(column_names, rows):
    print(r"\begin{center}")
    print(r"\begin{tabularx}{\textwidth}{|" + "X|"*len(column_names) + "}")
    print(r"\hline")
    print(" & ".join(rf"\multicolumn{{1}}{{|c|}}{{\textbf{{{sanitize_latex(col)}}}}}" for col in column_names), r"\\")

    print(r"\hline")
    for row in rows:
        print(" & ".join([sanitize_latex(str(x)) for x in row]), r"\\")
        print(r"\hline")

    print(r"\end{tabularx}")
    print(r"\end{center}")

def find_parameters(query):
    parameters = set()
    tokens = sqlparse.parse(query)[0]

    for token in tokens.flatten():
        if token.ttype is sqlparse.tokens.Name.Placeholder and token.value.startswith(":"):
            parameters.add(token.value[1:])

    return parameters

def process_script(cursor, script):
    script = "\n".join(list(filter(lambda line: not line.startswith("-- Task"), script.split("\n"))))
    queries = sqlparse.split(script)
    for query in queries:
        query.strip()
        if not query:
            continue

        print(r"\begin{minted}[breaklines]{sql}")
        print(query)
        print(r"\end{minted}")

        params = find_parameters(query)

        if query.endswith(";"):
            query = query[:-1].rstrip()

        filled_params = {}
        for param in params:
            print(f":{param}=", end="", file=stderr)
            filled_params[param] = input()
        

        cursor.execute(query, filled_params)
        if cursor.description is not None:
            column_names = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            print_table(column_names, rows)
        elif cursor.rowcount > 0:
            print(rf"\textbf{{{cursor.rowcount}}} {'row' if cursor.rowcount == 1 else 'rows'} affected.")
        else:
            print(rf"Statement executed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", "-q", required=True, help="path to query file")
    parser.add_argument("--author", "-a", required=True, help="e.g. <first_name> <last_name> <student_number>")
    parser.add_argument("--title", "-t", required=True, help="title of the document")

    args = parser.parse_args()

    scripts = parse_srcipts(args.query)
    print(f"Scripts found: {len(scripts)}", file=stderr)

    oracledb.init_oracle_client(lib_dir=DB_LIB_DIR)
    connection = None
    try:
        print("Connecting to the database... ", end="", file=stderr)
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
        )
        print("connected!", file=stderr)

        print_header(args.author, args.title)

        print(r"\begin{document}")
        print(r"\maketitle")

        for i, script in scripts:
            print(f"Running task {i}...\t", end="", file=stderr)
            with connection.cursor() as cursor:
                print(rf"\section*{{Task {i}}}")

                script = "".join(script)
                process_script(cursor, script)
                print(r"\pagebreak")

            print("done", file=stderr)

        print(r"\end{document}")
        return True


    except oracledb.Error as e:
        error, = e.args
        print(f"Database error occurred: {error.code} - {error.message}", file=stderr)
        return False

    finally:
        if connection:
            connection.close()
            print("Connection closed.", file=stderr)


if __name__ == "__main__":
    if main() == False:
        exit(-1)
