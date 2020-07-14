# Refugee Trends

This project builds on the work done by University of Oulu, University of Melbourne, and Harokopio University of Athens in their paper [Correlating Refugee Border Crossings with Internet Search Data](http://jultika.oulu.fi/files/nbnfi-fe201901222715.pdf). In that paper, they attempted to answer the question _Can Internet search data be used as a proxy to predict refugee  mobility?_. Per their findings, "Results indicate that the reuse of internet search data considerably improves the predictive power of the models." However, this research solely focused on refugees fleeing North Africa and the Middle East for Greece. This project aims to apply these techniques to refugees fleeing Somalia and South Sudan for Ethiopia.

![Refugee Correlation](imgs/architecture.png)


## Refugee Correlation

First, add your Google Translate `.json` credentials path to `config.ini`. You'll also need to `pip` install the `requirements.txt` file.

`refugee_correlation.py` provides a tool that uses Google Translate and Google Trends to assist a user in identification of terms that may be correlated with refugee arrivals. This currently supports refugee arrivals to Ethiopia from Somalia and South Sudan. The user selects a country of interest (Somalia or South Sudan) then inputs a term. That term can optionally be translated into Somali or Sudanese. Then it is checked against Google Trends for that country. A Pearson correlation coefficient is returned for the Google Trend time series correlation with refugee arrivals to Ethiopia.

![Refugee Correlation](imgs/refugee-correlation.gif)


## Building Trends Data

Once you have identified a set of target terms using `refugee_correlation.py` you can use `build_trends.py` to generate a `.csv` file that maps Google Trends for those terms with [UNHCR refugee data for Ethiopia](https://data2.unhcr.org/en/country/eth). This can be run with:

```
python3 build_trends.py
```

You will be asked to enter terms (which should be entered pre-translated). Leave the input blank if you have no more terms to enter. Finally, you'll be able to output your formatted refugee and trends file to a filename of your choosing.

## Building the Model

This requires you have R installed. You should run `Rscript model.R INPUT.csv` where `INPUT.csv` is the combined refugee/trend file you created in the prior step using `build_trends.py`.

This executes the model developed in [Correlating Refugee Border Crossings with Internet Search Data](http://jultika.oulu.fi/files/nbnfi-fe201901222715.pdf) using your custom input. The output is a comparison of model accuracies. For example:

```
########### RESULTS ###########
             Method  RMSE   MAE
1          Baseline 16.13 13.59
2 Linear Regression 12.16  8.88
3         Full tree 19.90 15.57
4       Pruned tree 16.13 13.59
5     Random forest 16.66 13.03
6               SVM 12.07  9.96
###############################
```