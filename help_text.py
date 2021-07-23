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
The solution is known and will be presented in the next vercion of application. Thank you for understanding!

#### *Universal BRDF data format*
BRDF file format is based on [json](https://www.json.org/json-en.html) syntax. I.e. it is a text file that stores data in dictionaries in the form of:

> `{key: value}`

where key is 'string' type and value can be 'string', 'number', 'array', 'True', 'False', 'Null' or 'object' i.e. another '{key: value}' structure.

Consortium agreed on following keys and structure in the BRDF file format:
>
```json
>BRDF file is an object that contains only two main keys "metadata" and "data"
>{
>   "metadata": "value is an object with keys describing metadata and static properties of BRDF dataset" *
>       {                                
>           "id":          "value is a globally unique id as a string",
>           "type":        "BRDF",
>           "name":        "file name as a string",
>           "timestamp":   "timestamp of measurement or simulation as a string in the format of 
>                           YYYY-MM-DDThh:mm:ss±hh:mm UTC corresponding to ISO8601 standard",
>           "provenance":  "value is a string or an object {key: number/string} with corresponding keys describing 
>                           the origin of the data i.e. institution, address, personell etc.",
>           "simulation":  "value is a string or an object {key: number/string} with corresponding keys describing 
>                           the mathematical/physical simulation model and its parameters used to produce BRDF data",
>           "system":      "value is a string or an object {key: number/string} with corresponding keys describing 
>                           the setup or instrumentation and its parameters used to measure BRDF data",
>           "sample":      "value is a string or an object {key: number/string} with corresponding keys describing 
>                           the virtual or actual sample used to produce BRDF data",
>           "environment": "value is a string or an object {key: number/string} with corresponding keys describing 
>                           the environmental conditions during BRDFmeasurement like pressure, temperature, 
>                           humidity, etc.",
>           "comments":    "value is a string or an object {key: number/string} with corresponding keys describing 
>                           any additional data related to BRDF measurement",
>           "any key":     "value is a string or an object {key: number/string} with corresponding keys describing
>                           any other information relevant to the BRDF data"
>       },
>       
>   "data": "value is an object with keys related to definition of BRDF function in spherical coordinates, 
>            variable properties of BRDF data and BRDF values themselves"
>       {
>           "variables": "value is an array of objects where each object desribes a variable
>                         that was changed during measurement or simulation - see example below"
>               [
>                   {"name":         "theta_i",  
>                    "type":         "number", 
>                    "unit":         "deg or rad",                     
>                    "description": "Illumination zenith angle of incidence",
>                    "any key":      "value as number or string"},                                             #1 **
>
>                   {"name":        "phi_i",    
>                    "type":        "number", 
>                    "unit":        "deg or rad",                     
>                    "description": "Illumination azimuthal angle of incidence",
>                    "any key":     "value as number or string"},                                              #2 **
>
>                   {"name":        "theta_r",  
>                    "type":        "number", 
>                    "unit":        "deg or rad",                     
>                    "description": "Viewing zenith angle",
>                    "any key":     "value as number or string"},                                              #3 **
>
>                   {"name":        "phi_r",    
>                    "type":        "number", 
>                    "unit":        "deg or rad",                     
>                    "description": "Viewing azimuthal angle",
>                    "any key":     "value as number or string"},                                              #4 **
>
>                   {"name":        "BRDF",     
>                    "type":        "number", 
>                    "unit":        "sr-1",                          
>                    "description": "Measured or simulated BRDF values",
>                    "any key":     "value as number or string"},                                              #5 **
>
>                   {"name":        "uBRDF",    
>                    "type":        "number", 
>                    "unit":        "sr-1",                          
>                    "description": "Uncertainty of measured or simulated BRDF values",
>                    "any key":     "value as number or string"},                                              #6 **
>
>                    ...
>
>                   {"name":        "any name 1", 
>                    "type":        "number" or "string", 
>                    "unit":        "corresponding unit",  
>                    "description": "short description of variable or its definition", 
>                    "any key":     "value as number or string"},                                              #M-1 
>
>                   {"name":        "any name 2", 
>                    "type":        "number" or "string", 
>                    "unit":        "corresponding unit",
>                    "description": "short description of variable or its definition", 
>                    "any key":     "value as number or string"},                                              #M
>               ],
>           "values": "value is an array with length N corresponding to number of measured BRDF points where
>				       each element is an array with length M corresponding to M varibles that were varied 
>				       during simulation/measurement"
>               [
>                   [number_1, number_2, number_3, number_4, ... number/string_M-1, number/string_M],          #1
>                   [number_1, number_2, number_3, number_4, ... number/string_M-1, number/string_M],          #2
>                    ...
>                   [number_1, number_2, number_3, number_4, ... number/string_M-1, number/string_M]           #N
>               ]
>       }
>}
>
>*  All keys in metadata are mandatory except any additional keys described as "any key". If there is no data
>    corresponding to the key, please use "NA" string. For example if data corresponds purely to measurement,
>    there shouldn't be any simulation data available and hence the field is "NA".
>
>** All objects within array of "variables" specified by this mark are mandatory and should be always present
>    even if the corresponding variables were constant during simulation or measurement. Numerical values of such 
>    variables should be fixed and repeated through all corresponding columns within 2D array of "values". 
>    Other objects within "variables" are not mandatory and if corresponding variables were constant it is
>    advised to specify this information under one of the "metadata" keys to avoid repeating information within 
>    2D array of "values"
```
>

File can have extension .json or .brdf.

File can be validated using following JSON Schema: [brdf_json_schema.json](https://jsoneditoronline.org/#right=local.yutupo&left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2Fbrdf_json_schema.json).

Example files (toggle code/tree options to study the file):
* [Example 1](https://jsoneditoronline.org/#right=local.yutupo&left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2FTest%2520BRDF%2520data%2520files%2FT08_example.brdf)
* [Example 2](https://jsoneditoronline.org/#right=local.yutupo&left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2FTest%2520BRDF%2520data%2520files%2Fprocessed_sand_data_v3.brdf)
* [Example 3](https://jsoneditoronline.org/#right=local.yutupo&left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2FTest%2520BRDF%2520data%2520files%2Fsand_stones_450_900.brdf)

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