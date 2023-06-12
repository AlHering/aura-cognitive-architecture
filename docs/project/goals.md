# Main Goal
The main goal of this projects - as already touched in the project's Abstract - is to build a code base (which can also be understood as a workbench) for developing and testing more complex AI-leveraging architectures, with special focus on the topic Cognitive Architecture and the role of dynamic interfaces.

To clarify, we can take a look at the architecture of [Emergent autonomous scientific research capabilities of large language models](https://arxiv.org/abs/2304.05332), which utilizes multiple transformer-model-based agents. With special focus on the interfacing towards external hardware with the help of API documentation researching, we can derive a few characteristics on the relevancy of interfaces under the question, whether a language model is the right tool for this job.
I would argue, that
- API documentations are very different in many metrics (length, depth, formulation, structuring, ...)
- especially with a focus on a specific topic and the need to actually provide and connect the hardware, the number of hardware resources and thus APIs should be limited
- only a subset of all functionality, provided by the hardware resource and thus explained in the documentation, might be of use for task completion
- errors at this point of the process can cause severe damage due to direct impact on the physical world
Would a static, human-made prompt component to explain the API usage achieve faster and better results while minimizing serious risks?
Can we optimize both, automation and stability/safety at the same time?
How fast can we react to changes in our hardware pool or APIs?

To sum up, many important questions and decisions are geared towards the interfaces, which makes them as important as the interfaced components.
Meanwhile, the paper above shows, how valuable, powerful and efficient such architectures can solve known and unkown problems. 

## Downstream Goals
The above specification is relatively broad since the fruther usage of the "workbench" should also be very broad. Therefore, for concepting, developing and testing components, a few more specific goals will be defined in the process.

### Developing and evaluating the migration of backend components from traditional algorithms to machine learning based approaches
#### Extracting product information from super market sources
The (first) specific project that will be used as an example for evaluating the "workbench" will be a scraping project for extracting product data, price data and special offers from a few common super markets in Germany. Right now this data is extracted from web sources, transformed and loaded into logic for determining "good offers" based on personal consumption habits. The customized web-scrapers are regularly under re-development since the sources (webside structure, infromation representation, barriers) change. Furthermore the logic involved is not very flexible. A good offer for the same product might be ignored or misinterpreted because of an unkown brand or changes in the product description. 

To simplify the process and therefore the underlying logic and code and to optimize the results, different machine learning components can be tested to interpret the product information, often given in natural language.