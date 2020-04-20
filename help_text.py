help_text_markdown = '''
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

Example files:
* [Example 1](/test_data_8.json)
* [Example 2](/test_data_9.json)
* [Example 3](/110119_1500-20_i0_A_NO_ADL.json)

'''