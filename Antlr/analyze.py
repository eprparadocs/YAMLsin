
def list_to_dict(input_list):
    result = {}
    for item in input_list:
        if len(item) != 2:
            raise ValueError("Each item in input list must have exactly 2 elements")

        key = item[0]
        value = item[1]

        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
            result[key] = list_to_dict(value)
        else:
            result[key] = value

    return result

def main():
    from argparse import ArgumentParser
    from os.path import isfile
    import sys

    parser = ArgumentParser(description='Convert list of lists from file to dictionary')
    parser.add_argument('input_file', help='Input file containing list of lists')
    args = parser.parse_args()

    if not isfile(args.input_file):
        print(f"Error: {args.input_file} is not a file", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, 'r') as f:
        content = eval(f.read())
        result = list_to_dict(content[0])
        print(result)

if __name__ == '__main__':
    main()
