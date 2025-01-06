This application generates jpg previews of .msg and .eml email files.

# Setup
install rye (or any other python pkg manager of choice, you'll have to install the dependencies yourself)

install rust (`brew install rust` or https://www.rust-lang.org/tools/install)

`rye sync`

# Starting the program (local)
`python src/main.py`


`curl -X POST -F "file=@path/to/your/email-file.msg" http://localhost:8082/converter --output output.jpg`


# Installing packages
`rye add <package-name>`

`rye sync`
