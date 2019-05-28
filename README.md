# IO2019
Virtual Machine manager for Software Engineering classes (IET 2019).

Used techonogy:
    
    Miniconda
    Python
    Flask
    Black (code formatter)


Conda environment update:
    
    conda env update --name IO2019-server -f=environment.yml
    
Conda update:

    conda update -y -n base -c defaults conda

Conda setup:
    
    Install Miniconda for your OS (linux/macOS) with 3.7 Python:
        https://docs.conda.io/en/latest/miniconda.html

    Create your Conda environment with command:
        conda env create -f environment.yml

    To activate environment in terminal type:
        conda activate IO2019-server #macOS
        source activate IO2019-server #linux
    
    Remember to activate your environment every time before work in terminal!
    
    

PyCharm:
    
    While configuring PyCharm project remeber to set your environment as conda
    Your interpreter should be the same as your environment interpreter

To configure generating mock data at startup, set variable:
- Unix

        export MOCK=1
        
- Windows

        set MOCK=1

To run app: 
        
        python app.py

To run tests: 
        
        py.test

To run python formatter for directory:
        
        black $DIR
        
To create database run 'init_db', with (standard):
        
        http://127.0.0.1:5000/init_db
