help_text_markdown_part_1 = '''
#### *About BiRDview*

***BiRDview*** is an open source web-application for visualization of _**B**idirectional **R**eflectance **D**istribution **F**unction_ (**BRDF**) measurement data.
It was developed as one of the results of Joint Research Project _**Bi**directional **R**eflectance **D**efinitions_ 
([BiRD](https://www.birdproject.eu/), JRP 16NRM08) supported by [EMPIR](https://www.euramet.org/research-innovation/research-empir/) 
initiative of [EURAMET](https://www.euramet.org/about-euramet/).

Application is written in Python using [Plotly](https://plotly.com/) [Dash](https://dash.plotly.com/) 
open source library and the code can be found [here](https://github.com/BiRD-project/BiRD_view). 

Current version of application allows to open and view files only in the file format developed and agreed by BiRD consortium.

NB! Heroku servers have timeout of 30s. This may cause application to fail to upload very large files.
The solution is known and will be introduced in the next version of application. Thank you for understanding!

#### *Universal BRDF data format*
BRDF file format is based on [json](https://www.json.org/json-en.html) syntax. I.e. it is a text file that stores data in dictionaries in the form of:

> `{key: value}`

where key is 'string' type and value can be 'string', 'number', 'array', 'True', 'False', 'Null' or 'object' i.e. another '{key: value}' structure.

Consortium agreed on following keys and structure in the BRDF file format that are thoroughly described in following [article](https://doi.org/10.1002/col.22790) 
with [supporting materials](https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fcol.22790&file=col22790-sup-0001-supinfo.zip) and 
[documentation](https://bird-project.github.io/BRDF_JSON_schema_docs) web-page.

File can have extension .json or .brdf.

File can be validated using following JSON Schema: [brdf_json_schema_v1.0.json](https://github.com/BiRD-project/BiRD_view/blob/master/BRDF_JSON_schema/brdf_json_schema_v1.0.json).

Example file (toggle code/tree options to study the file):
* [Example 1](mhttps://jsoneditoronline.org/#right=local.yutupo&left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2FTest%2520BRDF%2520data%2520files%2Fexample.brdf)

#### *Quick guide*

##### *Uploading file*
To upload the BRDF file in the **"Applet"** tab locate upload field where you can either drag and drop files or open a 
file selection dialogue to choose files to be opened. Uploading of multiple files is allowed and "loading" animation
will be shown until all files are loaded. Uploaded file's/files' name will appear in the dropdown menu below upload field.
Uploading of files with the same name is also allowed. In this case a suffix "_copy_N" will be added
to file name where N corresponds to number of copies. 

Click on gif below to see uploading procedure example:

'''

help_text_markdown_part_2 = '''

##### *Selecting uploaded file*

To select one of the uploaded files as an active, click dropdown menu with file names and select file by clicking on its 
file name. After that menu with file parameters as well as figures will be updated to correspond to selected file.

Click on gif below to see file selecting procedure example:

'''

help_text_markdown_part_3 = '''

##### *Navigating through data parameters and figures*

By definition BRDF data has more than 3 dimensions that makes it impossible to depict all the data on a single figure.
For this reason smaller pieces of data should be selected and depicted on multiple figures. In BiRD view this can be performed
by using dropdown menus located under file selection dropdown. There, corresponding to BRDF file format, you can select:
incidence zenith angle, incidence azimuthal angle, viewing zenith angle, viewing azimuthal angle and any additional
available parameters (from top to bottom). All parameters remain unique to every file. That means when you change parameters for one file,
they are not changed for other files and applet remembers choices for each file. 

Choices can be made by clicking corresponding dropdown and selecting desired parameter value. Click on the gif below to
see an example.

'''

help_text_markdown_part_4 = '''

Metadata of the file can be acessed through a "Metadata" tab within file menu:

'''

help_text_markdown_part_5 = '''

Changing data parameters will update the figures located on the right from file menu dropdowns'.
There are currently two tabs that allow you to explore BRDF data in terms of raw values and 
CIELAB values calculated from them.

There are four figures for BRDF data viewing. First - top left - provides the 3D shape of BRDF at specified
incidence zenith and azimuthal angles as well as all other parameters. Changing these parameters will cause figure to update.
Dots on the figure represent measured data points and by hovering the mouse over them one can see measured values.
Color coded surface drawn though measured points gives an idea about the shape of the BRDF.

'''

help_text_markdown_part_6 = '''

Bottom left figure represents the projection of 3D plot to the XY plane and converted to the polar plot. By rotating
plot one can select viewing azimuthal angle in parallel with corresponding dropdown menu. This selects a plane for 2D BRDF
plot located  on the right (bottom-right).

'''

help_text_markdown_part_7 = '''

2D BRDF plot shows you the BRDF at specified incidence zenith, azimuthal angles, additional parameters and selected
viewing azimuthal angle. Changing these parameters will cause graph to update. By clicking on a point located shown on this graph
you can see the reflectance spectrum at this point. 

'''

help_text_markdown_part_8 = '''

Last graph located at the upper right corner can show 2D BRDF dependence on any parameter selected as X including additional parameters.
To select parameter as X use dropdown menu named "Select variable as X". Upon selection graph will be updated and desired
BRDF dependence on selected parameter will be shown.

'''

help_text_markdown_part_9 = '''

##### *Viewing data from multiple files at the same time*

On 2D plots user can plot and compare data from one and the same file or from different files. To do that one needs to 
take a snapshot of file menu state by pressing "Snap state" button. When state is snapped BiRDview will remember it and plot it 
alongside any other state from file menu or other sanaped states. 

'''

help_text_markdown_part_10 = '''

##### Basics on figures' controls

As was mentioned before, BiRDview app uses plotly graphing library that allows to create quite interactive figures.
You can move graphs, rotate them, zoom to specific areas, get information by hovering mouse over data points and much
more. Don't be afraid to learn by trial and remember that you can return to initial states either by double-clicking on 
the plot or by using home button on the figure menu that appears in the upper right corner of the graphs when you hover
your mouse over them. In menu you can also find other useful option and save figures as .png files.

'''