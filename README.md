## GUI for .hp files
- Instead of parsing through individual ```.hp``` files, this GUI allows you to view the entire database in a more user-friendly manner. 
- The user can trash individual images. Note these files are recoverable if the user copies the ```.hp``` file before trashing. 
## Usage
1. To install required packages run ```pip install requirements.txt``` in your venv or conda environment
2. Place your ```.hp``` files at [patterns](patterns)
3. Run the script [GUI.py](GUI.py)
4. ```Browse``` for your file, ```Plot``` to view the data. To navigate between images use the arrow buttons. To adjust the contrast of the image to better view the diffraction spots use the min and max input boxes.

> [!CAUTION]
> Using ```Trash``` will delete the current image you are viewing. This is irreversible unless you toggle the ```Copy``` button before plotting your dataset.

\
![GUI](gitignore/demo.png)