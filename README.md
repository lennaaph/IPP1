# Principles of programming languages - 1.project

### Description:
This Python script parses and validates a specific language (IPPcode24) and generates an XML representation of the parsed instructions.

### Usage:
```bash
python3.10 parse.py [options]
```

### Options:
- `-h, --help`: Displays help message and exits with code 0.

### Functionality:
The script reads input either from a file or stdin, validates each instruction according to the IPPcode24 specification, and generates XML output representing the parsed instructions.

### Dependencies:
- Python 3.10
- `xml.etree.ElementTree`
- `xml.dom.minidom`

### Example Usage:
To parse and validate instructions from a file:
```bash
python3.10 parse.py < input_file.ipp
```

### Notes:
- Ensure the input file conforms to the IPPcode24 specification.
- Errors are reported with specific error codes for easy debugging.
