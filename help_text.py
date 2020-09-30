help_text_markdown_part_1 = '''
#### *About BiRDview*

***BiRDview*** is an open source web-application for visualization of _**B**idirectional **R**eflectance **D**istribution **F**unction_ (**BRDF**) measurement data.
It was developed as one of the results of Joint Research Project _**Bi**directional **R**eflectance **D**efinitions_ 
([BiRD](https://www.birdproject.eu/), JRP 16NRM08) supported by [EMPIR](https://www.euramet.org/research-innovation/research-empir/) 
initiative of [EURAMET](https://www.euramet.org/about-euramet/).

Application is written in Python using [Plotly](https://plotly.com/) [Dash](https://dash.plotly.com/) 
open source library and the code can be found [here](https://github.com/BiRD-project/BiRD_view_v4). 

Current version of application allows to open and view files only in the file format developed and agreed by BiRD consortium.

#### *BRDF file format*
BRDF file format is based on [json](https://www.json.org/json-en.html) syntax. I.e. it is a text file that stores data in dictionaries in the form of:

> `{key: value}`

where key is 'string' type and value can be 'string', 'number', 'array', 'True', 'False', 'Null' or 'object' i.e. another '{key: value}' structure.

Consortium agreed on following keys and structure in the BRDF file format:
>
```py
>{
>  head:{                        # Header section. Has quite loose definition. Keys and contents may vary freely, but 
>                                # must follow json syntax and data types.
>                                
>          date: "dd-mm-yyyy",   # Value --> String. Date format is fixed as shown here.
>          
>          any key: any data     # For example, detection slid angle, list of authors, institute or organization where 
>                                # measurements were made etc.
>       },
>       
>  data:{                                        # Data section has a strict definition. All keys should remain as 
>                                                # specified and adding other keys is not allowed.
>
>          #==================================== Illumination properties keys ====================================
>
>          #------------------------------------ Primary axis ----------------------------------------------------
>                                                
>          wavelengths: [λ1, λ2, ..., λN],       # Value --> array of numbers. Primary axis or row vector for data.
>                                                # Wavelengths at which each data row was measured.
>
>          #------------------------------------ Non-primary axes ------------------------------------------------
>
>          pol: [pol1, pol2, ..., polM],         # Value --> array of strings. Names can be any  - i.e. 'p','s' or 
>                                                # 'p-polarized', 's-polarized' or any other would be read correctly.
>                                                # NB! If you have two or more different values for polarization,
>                                                # parser will automatically calculate average of all of them.
>                                                # this feature is cannot be disabled at the moment, but it doesn't
>                                                # disturb BRDF viewing in any scenario. If you used unpolarized light,
>                                                # insert 'u' or 'unpolarized' respectively. 
>
>          theta_i: [θi1, θi2, ..., θiM],        # Value --> array of numbers. Illumination incidence zenith angle. 
>                                                # Can vary +/-90 deg around normal to the sample.
>                                                
>          phi_i: [Φi1, Φi2, ..., ΦiM],          # Value --> array of numbers. Illumination incidence azimuthal angle. 
>                                                # Can vary 0 to 360 deg. Depends on measurement procedure.
>                                                # If theta_i is measured only from 0 to 90, then it is wise to use 
>                                                # range 0 to 360 deg.
>                                                # If theta_i is measured +/-90 around normal, i.e. you measure 
>                                                # simultaneously data at theta_i and theta_i + 180,
>                                                # then it is better to use range 0 to 180 deg to avoid data overlapping.
>
>          #==================================== Viewing properties keys =========================================
>
>          #------------------------------------ Non-primary axes ------------------------------------------------
>                                                
>          theta_v: [θv1, θv2, ..., θvM],        # Value --> array of numbers. Illumination viewing zenith angle. 
>                                                # Can vary +/-90 deg around normal to the sample.
>                                                
>          phi_v: [Φv1, Φv2, ..., ΦvM],          # Value --> array of numbers. Illumination viewing azimuthal angle. 
>                                                # Can vary 0 to 360 deg. Depends on measurement procedure. 
>                                                # If theta_i is measured only from 0 to 90, then it is wise to use range
>                                                # 0 to 360 deg. If theta_i is measured +/-90 around normal, i.e. you 
>                                                # measure simultaneously data at theta_v and theta_v + 180,
>                                                # then it is better to use range 0 to 180 deg to avoid data overlapping.
>                                                #
>                                                # NB! In current version, the projection heatmap polar plot won't operate
>                                                # correctly if ou measured twice one and the same plane. It is common if 
>                                                # you have measured BRDF at phi_v = 0 in the beginning of measurement and
>                                                # 180 or 360 in the end of the measurement depending if theta_v varies 
>                                                # from +/-90 or 0 to 90 around normal).
>                                                # Try to avoid this by manually selecting which of two datasets in 
>                                                # the same plane to leave in the file.
>                                                # If you would like to test repeatability by measuring multiple data 
>                                                # sets in one plane, try to separate data to different file int present 
>                                                # format. That way you would be able to analyze them while seeing all 
>                                                # graphs correctly.
>                                                
>          #==================================== Data points =====================================================
>
>          data: [[point1, point2, ..., pointM], # 1    # Value --> array of arrays of numbers.
>                 [point1, point2, ..., pointM], # 2    # 2D array of measured BRDF values corresponding to illumination
>                 ...,                                  # and viewing properties defined above. There are N rows 
>                 [point1, point2, ..., pointM]] # N    # corresponding to the number of values in primary axis, i.e. 
>                                                       # number of wavelengths. Each row contains an array with the length
>                                                       # of M corresponding to the number of values in all non-primary axes.
>  }
>}
```
>

File can have extension .json or .brdf.

Clean view of file format:

>
```py
>{
>  head:{                       
>          date: "dd-mm-yyyy",   
>          any key: any data     
>       },
>  data:{                                                                      
>          wavelengths: [λ1, λ2, ..., λN],      
>          pol: [pol1, pol2, ..., polM],         
>          theta_i: [θi1, θi2, ..., θiM],       
>          phi_i: [Φi1, Φi2, ..., ΦiM],         
>          theta_v: [θv1, θv2, ..., θvM],        
>          phi_v: [Φv1, Φv2, ..., ΦvM],          
>          data: [[point1, point2, ..., pointM], # 1    
>                 [point1, point2, ..., pointM], # 2    
>                 ...,                                  
>                 [point1, point2, ..., pointM]] # N                                                     
>       }
>}
```
>

Example files (toggle code/tree options to study the file):
* [Example 1](https://jsoneditoronline.org/#left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2Ftest%2520json%2520files%2Ftest_data_8.json&right=local.yutupo)
* [Example 2](https://jsoneditoronline.org/#left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2Ftest%2520json%2520files%2Ftest_data_9.json&right=local.yutupo)
* [Example 3](https://jsoneditoronline.org/#left=url.https%3A%2F%2Fraw.githubusercontent.com%2FBiRD-project%2FBiRD_view%2Fmaster%2Ftest%2520json%2520files%2F110119_1500-20_i0_A_NO_ADL.json&right=local.yutupo)

#### *Quick guide*

##### *Uploading file*
To upload the BRDF file in the **"Applet"** tab locate upload field where you can either drag and drop files or open a 
file selection dialogue to choose files to be opened. Uploading of multiple files is allowed and "loading" animation
will be shown until all files are loaded. Uploaded file's/files' name will appear in the dropdown menu below upload field.
In current version uploading of files with the same name is also allowed. In this case a suffix "_copy_N" will be added
to file name where N corresponds to number of copies. This allows to compare data from one and the same file with itself 
when it is needed.

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
wavelength, polarization, incidence zenith angle, incidence azimuthal angle, viewing zenith angle, and viewing azimuthal angle 
(from left to right). There are also two options related to color analysis that allow you to select Illuminant and Observer 
to estimate CIELAB values. These options are not related to the uploaded files and default they are "D65" and 
"CIE 1931 2 Degree Observer". All parameters remain unique to every file. That means when you change parameters for one file,
they are not changed for other files and applet remembers choices for each file.

Choices can be made by clicking corresponding dropdown and selecting desired parameter value. Click on the gif below to
see an example.

'''

help_text_markdown_part_4 = '''

If you forget which dropdown changed the parameter you need, you can always hover the mouse over dropdown and a quick tip will appear:

'''

help_text_markdown_part_5 = '''

Changing data parameters will update the figures located underneath dropdowns' menu.
There are currently two tabs that allow you to explore BRDF data in terms of raw values and 
CIELAB values calculated from them.

There are four figures for BRDF data viewing. First - top left - provides the 3D shape of BRDF at specified
wavelength, polarization, incidence zenith and azimuthal angles. Changing these parameters will cause figure to update.
Dots on the figure represent measured data points and by hovering the mouse over them one can see measured values.
Color coded surface drawn though measured points gives an idea about the shape of the BRDF.

'''

help_text_markdown_part_6 = '''

Bottom left figure represents the projection of 3D plot to the XY plane and converted to the polar plot. By rotating
plot one can select viewing azimuthal angle in parallel with corresponding dropdown menu. This selects a plane for 2D BRDF
plot located  on the right (bottom-right).

'''

help_text_markdown_part_7 = '''

2D BRDF plot shows you the BRDF at specified wavelength, polarization, incidence zenith, azimuthal angles and selected
viewing azimuthal angle. Changing these parameters will caus graph to update. By clicking on a point located shown on this graph
you can see the reflectance spectrum at this point. 

'''

help_text_markdown_part_8 = '''

BRDF spectrum at specified polarization, incidence zenith, azimuthal angles and selected
viewing azimuthal and zenith angles is depicted in top right figure. It gives an idea whether the measured
sample changes its color under different illumination and/or viewing circumstances or not. This spectrum is
used for further color and CIELAB values calculations.

##### *Viewing data from multiple files at the same time*

If one wants to view and compare data of selected file with some other file that will be selected in the future,
one should place a check mark in the checkbox named "visible" and located on the right from file selection dropdown.
In this case, when other file will be selected data from file marked as visible will appear on the 2D BRDF and 
BRDF spectrum plots. This feature is disabled for 3D and projection figures since it will disturb analysis rather than
help it while slowing down the app.

'''

help_text_markdown_part_9 = '''

##### Basics on figures' controls

As was mentioned before, BiRDview app uses plotly graphing library that allows to create quite interactive figures.
You can move graphs, rotate them, zoom to specific areas, get information by hovering mouse over data points and much
more. Don't be afraid to learn by trial and remember that you can return to initial states either by double-clicking on 
the plot or by using home button on the figure menu that appears in the upper right corner of the graphs when you hover
your mouse over them. In menu you can also find other useful option and save figures as .png files.

'''