# Read variables from 'Variables_NIF.txt'
with open('Variables_NIF.txt', 'r') as f:
    variables_lines = f.readlines()

def format_number(value, is_integer=False, is_halflife=False):
    """
    Formats a number in scientific notation:
    - Integer (release group): plain integer, no scientific notation
    - Half-life: 10 decimal places (X.XXXXXXXXXXE+XX)
    - Other numbers: 4 decimal places (X.XXXXE+XX)
    """
    if is_integer:
        return str(int(float(value)))

    val = float(value)
    if val == 0:
        if is_halflife:
            return "0.0000000000E+00"
        else:
            return "0.0000E+00"

    if is_halflife:
        formatted = f"{val:.10E}"
    else:
        formatted = f"{val:.4E}"

    return formatted

# Template structure — no blank line between nuclides
# Each nuclide block has exactly 9 lines
template = """ Nuclide {0}:
 {1}
  {2}
  {3}
  {4}
  {5}
 {6}     {7}
 {8}     {9}
 {10}     {11}"""

# Count nuclides (non-blank lines)
num_nuclides = len([l for l in variables_lines if l.strip()])

# Write output file 'i_SMR.NIF'
with open('i_SMR.NIF', 'w', newline='\r\n') as output_file:
    # Write header
    output_file.write(' Nuclide Inventory Name:\n')
    output_file.write(' Normalized i_SMR 530.4 MWth Core Inventory\n')
    output_file.write(' Power Level:\n')
    output_file.write('  0.1000E+01\n')
    output_file.write(' Nuclides:\n')
    output_file.write(f'  {num_nuclides}\n')

    for idx, line in enumerate(variables_lines):
        variables = line.strip().split()

        formatted_vars = []
        for i, var in enumerate(variables):
            if i == 0:             # Nuclide number (e.g. 001)
                formatted_vars.append(var)
            elif i == 1:           # Element name (e.g. Xe-131m)
                formatted_vars.append(var)
            elif i == 2:           # Release group (plain integer)
                formatted_vars.append(format_number(var, is_integer=True))
            elif i == 3:           # Half-life — 10 decimal places
                formatted_vars.append(format_number(var, is_halflife=True))
            elif i in [4, 5]:      # Mass number, activity — 4 decimal places
                formatted_vars.append(format_number(var))
            elif i in [6, 8, 10]:  # Decay daughter names
                formatted_vars.append(var)
            elif i in [7, 9, 11]:  # Decay daughter branching ratios — 4 decimal places
                formatted_vars.append(format_number(var))
            else:
                formatted_vars.append(var)

        filled_template = template.format(*formatted_vars)
        output_file.write(filled_template + "\n")

print("File 'i_SMR.NIF' created successfully.")
print("✓ Half-life: 10 decimal places (X.XXXXXXXXXXE+XX)")
print("✓ Other numbers: 4 decimal places (X.XXXXE+XX)")
print("✓ No blank lines between nuclides")
