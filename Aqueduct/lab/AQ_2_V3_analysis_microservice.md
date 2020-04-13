# Point analysis endpoint definition

**Repo**: ```https://github.com/resource-watch/aqueduct-analysis-microservice``` 

**GET**:  ```<api-url>/aqueduct/analysis?geostore=<geostore>&analysis_type=<analysis type>&wscheme=<weight scheme>&year=<year>&change_type=<changetype>&indicator=<indicator>&scenario=<scenario>``` 

**Example**: `0.0.0.0:9000/v1/aqueduct/analysis?geostore=3180551e745d2977a0ee51ca85118fe3&analysis_type=projected&month=1&wscheme='[0.,0.25,0.5,1.,1.,1.,null,1.,1.,0.25,1.,1.,1.]'&year=2030&change_type=change_from_baseline&indicator=water_stress&scenario=business_as_usual`

The parameters are: 

- **geostore** =  3180551e745d2977a0ee51ca85118fe3

     geostore id of a MultiPoint type geometry. 

- **analysis_type** = {annual, monthly, projected, custom}
    - *annual*: Analysis for the annual baseline indicators
    - *monthly*: Analysis for the monthly baseline indicators
    - *projected*: Analysis for the  annual projected indicators
    - *custom*: Analysis for the  annual projected indicators
    
- **month** = integers from 1 to 12.

     this parameter is only used for the *monthly* indicators.
     
- **wscheme** = '[0.,0.25,0.5,1.,1.,1.,null,1.,1.,0.25,1.,1.,1.]'

     list with the 13 indicators' weights. weight can take the following values: {null, 0.25, 0.5, 1, 2, 4}. This parameter is only use for the *custom* analysis.

- **year** = {2030, 2040}

     projection years. This parameter is only use for the *projected* analysis.
     
- **change_type** = {future_value, change_from_baseline}
    - *future_value*: Absolute value of the selected indicator
    - *change_from_baseline*: Change from baseline of the selected indicator

     This parameter is only use for the *projected* analysis.
     
- **indicator** = {water_stress, seasonal_variability, water_supply, water_demand}
    - *water_stress*: The ratio of water use to supply.
    - *seasonal_variability*: The variability of water supply between the months of the year.
    - *water_supply*: Water supply. 
    - *water_demand*: Water demand.

     This parameter is only use for the *projected* analysis.