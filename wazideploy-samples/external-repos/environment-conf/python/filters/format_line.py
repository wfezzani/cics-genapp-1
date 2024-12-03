## format a line and ensure continuation char atcolumn 72.
## line is the statement to be formatted.
## max_line_length is the maximum length of a line.
## start_text_at is the length of the indentation.
## last_line indicates if the statement is the last oneof a group of
## parameters. The last one does not need the continuation character.
## $suffix is the continuation character.
def format_line(line, max_line_length, start_text_at, last_line, prefix = '', suffix = ''):
    formatted_str = ''
    max_line_length = int(max_line_length)
    start_text_at = int(start_text_at)
    line = str(line)
    if len(line) <= max_line_length:
        formatted_str += line
        str_to_format_length = len(line)
        formatted_str = '{line: <{max_len}}'.format(line=formatted_str, max_len=max_line_length)
        if not last_line:
            formatted_str += suffix
    else:
        formatted_str = make_indent(line, max_line_length, start_text_at, last_line, prefix, suffix)
    return formatted_str

## handle indentation if JCL statement does notfit in 71 chars
## line is the statement to be formatted
## max_line_length is the maximum length of a line.
## start_text_at is the length of the indentation.
## last_line indicates if the statement is the last oneof a group of
## parameters. The last one does not need the continuation character.
## suffix is the continuation character.
def make_indent(line, max_line_length, start_text_at, last_line, prefix, suffix):
    if len(line) < max_line_length:
        formatted_str = '{line: <{max_len}}'.format(line=line, max_len=max_line_length)
        if not last_line:
            formatted_str += suffix
    else:
        formatted_str = line[:max_line_length] + suffix + '\n'
        line_remaining = prefix + (' ' * int(start_text_at)) + line[max_line_length:]
        formatted_str += make_indent(line_remaining, max_line_length, start_text_at, last_line, prefix, suffix)
    return formatted_str