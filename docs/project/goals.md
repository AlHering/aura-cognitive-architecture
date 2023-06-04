# Main Goal
The main goal of this projects - as already touched in the project's Abstract - is to build a code base (which can also be understood as a workbench) for developing and testing more complex AI-leveraging architectures, with special focus on the topic Cognitive Architecture and the role of dynamic interfaces.

## Downstream Goals
The above specification is relatively broad since the fruther usage of the "workbench" should also be very broad. Therefore, for concepting, developing and testing components, a few more specific goals will be defined in the process.

### Developing and evaluating the migration of backend components from traditional algorithms to machine learning based approaches
#### Extracting product information from super market sources
The (first) specific project that will be used as an example for evaluating the "workbench" will be a scraping project for extracting product data, price data and special offers from a few common super markets in Germany. Right now this data is extracted from web sources, transformed and loaded into logic for determining "good offers" based on personal consumption habits. The customized web-scrapers are regularly under re-development since the sources (webside structure, infromation representation, barriers) change. Furthermore the logic involved is not very flexible. A good offer for the same product might be ignored or misinterpreted because of an unkown brand or changes in the product description. 

To simplify the process and therefore the underlying logic and code and to optimize the results, different machine learning components can be tested to interpret the product information, often given in natural language.