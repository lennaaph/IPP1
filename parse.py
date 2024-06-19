# IPP - 1.úloha
# Phamová Thu Tra - xphamo00
# VUT FIT 2024

import sys
import re
import codecs
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM


class Argument():
    def if_help(argv):
        if len(argv) == 2 :
            # help output
            help_header = "IPP2024 parser\nUsage: python3.10 parse.py [--help]\n\n"
            help_msg = "Options:\n-h, --help : show help message and exit with 0\n"
            
            if argv[1] == "--help" or "-h" in argv:
                sys.stdout.write(help_header + help_msg)
                sys.exit(0)
            else:
                sys.stdout.write(help_header)
                Instructions.error_msg("Error: Wrong/missing parameters.\n", 10)
            
    def check_file():
        # check if there is a file
        if not sys.stdin.isatty():
            # read the file
            file = sys.stdin.read()
            
            # check if the input is empty
            if not file.strip():
                Instructions.error_msg("Error: Wrong/missing header in file.\n", 21)
            
            return file
        else:
        # no file found
            Instructions.error_msg("Error: No file detected.\n", 11)

class Instructions:
    def error_msg(err_msg, err):
        sys.stderr.write(err_msg)
        sys.exit(err)
    
    def error_arg_num(line, num):
        if len(line) != num:
            Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
    
    def label_check(word):
        label_name = r"^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$"
        if not re.match(label_name, word):
            return False

        return True
    
    def var_check(word):
        index = 0
        var = word.split("@", 1)
        Instructions.error_arg_num(var, 2)
        
        reg_frame = r"^(LF|TF|GF)$"
        if not (re.match(reg_frame, var[index]) and Instructions.label_check(var[index+1])):
            return False

        return True
            
    def symb_check(word):
        index = 0
        symb = word.split("@", 1)
        Instructions.error_arg_num(symb, 2)
        
        # regexes for each symbol-type
        reg_int = r"^[-+]?(\d+|(0x[0-9a-fA-F]+)|(0o[0-7]+))$"
        reg_bool = r"^(true|false)$"
        reg_const = r"^([^\s#\\]|\\[0-9]{3})*$"
        
        # checks if it is variable or constant
        if Instructions.var_check(word) :
            return 'var' # returning this for later xml output
        
        elif symb[index] == 'int' :
            if not re.match(reg_int, symb[index+1]) : return False
        elif symb[index] == 'bool' :
            if not re.match(reg_bool, symb[index+1]) : return False
        elif symb[index] == 'string' :
            if not re.match(reg_const, symb[index+1]) : return False
        elif symb[index] == 'nil' :
            if not symb[index+1] == 'nil' : return False
        else:
            return False
        
        return symb # returning this for later xml output
        
    def type_check(word):
        type = r"^(int|bool|string)$"
        if not re.match(type, word):
            return False

        return True        

    def parse(file):
        # removes comments and empty lines in file
        clean_cmt = re.sub(r"#.*", "", file)
        clean_f = re.sub(r"^\s*", "", clean_cmt, flags=re.MULTILINE)
        
        # goes through each line
        divided = clean_f.splitlines()
        for line_index, line in enumerate(divided, 1) :
            newline = line.split()
            # goes through each item in a line
            for index, word in enumerate(newline, 1):
                
            # grouping based on needed arguments for easier approach
                group_none = ("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK")
                group_label = ("CALL", "LABEL", "JUMP")
                group_var = ("DEFVAR", "POPS")
                group_symb = ("PUSHS", "WRITE", "EXIT", "DPRINT")
                group_var_symb = ("MOVE", "NOT", "INT2CHAR", "STRLEN", "TYPE")
                group_var_type = ("READ")
                group_var_symb_symb = ("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR")
                group_label_symb_symb = ("JUMPIFEQ", "JUMPIFNEQ")

            # check header
                keyword = word.upper()
                if line_index == 1 :
                    if keyword == ".IPPCODE24" :
                        # check if header is only item in the line
                        Instructions.error_arg_num(newline, 1)
                    else:
                        Instructions.error_msg("Error: Wrong/missing header in file.\n", 21)
                    break
                
            # error for none-opcode
                elif line_index != 1 and (not re.match(r"^[a-zA-Z0-9]+$", keyword)):
                    Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                    break
                
            # check opcode ------
                elif keyword in group_none :
                    # checks number of needed arguments
                    Instructions.error_arg_num(newline, 1)
                    # saves opcode in xml output
                    Xml.instruction(line_index, keyword)
                    # no arguments to save for xml output
                    break
                    
                elif keyword in group_label:
                    # checks number of needed arguments
                    Instructions.error_arg_num(newline, 2)
                    # saves opcode in xml output
                    instruction = Xml.instruction(line_index, keyword)
                    
                    # checks for correctness of each argument
                    if not Instructions.label_check(newline[index]) :
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                    
                    # saves arguments in xml output
                    Xml.attribute('label', newline[index], index, instruction)
                    break
                
                elif keyword in group_var:
                    Instructions.error_arg_num(newline, 2)
                    instruction = Xml.instruction(line_index, keyword)
                    
                    if not Instructions.var_check(newline[index]) :
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                        
                    Xml.attribute('var', newline[index], index, instruction)
                    break
                
                elif keyword in group_symb:
                    Instructions.error_arg_num(newline, 2)
                    instruction = Xml.instruction(line_index, keyword)
                    
                    if not Instructions.symb_check(newline[index]) :
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                    
                    Xml.symb_parse(newline[index], index, instruction)
                    break
                
                elif keyword in group_var_symb:
                    Instructions.error_arg_num(newline, 3)
                    instruction = Xml.instruction(line_index, keyword)
                    
                    if not (Instructions.var_check(newline[index]) and Instructions.symb_check(newline[index+1])) : 
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                        
                    Xml.attribute('var', newline[index], index, instruction)
                    Xml.symb_parse(newline[index+1], index+1, instruction)
                    break
                
                elif keyword in group_var_type:
                    Instructions.error_arg_num(newline, 3)
                    instruction = Xml.instruction(line_index, keyword)
                    
                    if not (Instructions.var_check(newline[index]) and Instructions.type_check(newline[index+1])) : 
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                        
                    Xml.attribute('var', newline[index], index, instruction)
                    Xml.attribute('type', newline[index+1], index+1, instruction)
                    break
                
                elif keyword in group_var_symb_symb:
                    Instructions.error_arg_num(newline, 4)
                    instruction = Xml.instruction(line_index, keyword)
                    
                    if not (Instructions.var_check(newline[index]) and Instructions.symb_check(newline[index+1]) and Instructions.symb_check(newline[index+2])) :
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                    
                    Xml.attribute('var', newline[index], index, instruction)
                    Xml.symb_parse(newline[index+1], index+1, instruction)
                    Xml.symb_parse(newline[index+2], index+2, instruction)
                    break
                
                elif keyword in group_label_symb_symb:
                    Instructions.error_arg_num(newline, 4)
                    instruction = Xml.instruction(line_index, keyword)
                    
                    if not (Instructions.label_check(newline[index]) and Instructions.symb_check(newline[index+1]) and Instructions.symb_check(newline[index+2])) :
                        Instructions.error_msg("Error: Lexical/syntax error of argument/s.\n", 23)
                    
                    Xml.attribute('label', newline[index], index, instruction)
                    Xml.symb_parse(newline[index+1], index+1, instruction)
                    Xml.symb_parse(newline[index+2], index+2, instruction)
                    break
                
            # end check opcode ------
                else:
                    Instructions.error_msg(f"Error: Wrong/unknown opcode.\n", 22)

class Xml:
    def program() :
        program = ET.Element('program', attrib={"language": "IPPcode24"})
        return program
    
    def instruction(line_index, item) :
        instruction = ET.SubElement(program, 'instruction', {"order": str(line_index-1), "opcode": item.upper()})
        return instruction
        
    def attribute(type, text, index, instruction) :
        attribute = ET.SubElement(instruction, f"arg{index}", {"type": type})
        attribute.text = text
        
    def symb_parse(word, index, instruction) :
        # finds out if it is a variable or a constant
        symb = Instructions.symb_check(word)
        if symb == 'var' :
            Xml.attribute('var', word, index, instruction)
        else:
            symb_part = word.split("@", 1)
            Xml.attribute(symb_part[0], symb_part[1], index, instruction)
    
    def printing() :
        xml_string = ET.tostring(program)
        output = DOM.parseString(xml_string).toprettyxml(encoding='UTF-8')
        sys.stdout.write(codecs.decode(output))


if __name__ == "__main__":
    # check arguments
    Argument.if_help(sys.argv)
    file = Argument.check_file()

    # starts xml document for saving data from parser
    program = Xml.program()
    
    Instructions.parse(file)
    
    Xml.printing()