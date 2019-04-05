# IO2019
Virtual Machine manager for Software Engineering classes (IET 2019).

Used techonogy:
    
    - Miniconda
    - Python
    - Flask
    - Black (code formatter)


Developement configuration:

Conda:
    
    Install Miniconda for your OS (linux/macOS) with 3.7 Python:
        https://docs.conda.io/en/latest/miniconda.html

    Create your Conda environment with command:
        conda env create -f environment.yml

    To activate environment in terminal type:
        conda activate IO2019-server #macOS
        source activate IO2019-server #linux

    Update your environment with running the script: (update ONLY for "I02019-server" environment)
        ./update.sh
    
    *Remember to activate your environment every time before work!*
    
    

PyCharm:
    
    While configuring PyCharm project remeber to set your environment as conda
    Your interpreter should be the same as your environment interpreter

To run app: 
        
        python app.py

To run tests: 
        
        py.test

To run python formatter for directory:
        
        black $DIR
