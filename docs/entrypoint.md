# Abstract
The very broad field of artificial intelligence (AI) is rapidly progressing, driven by advancements in hardware, algorithms, and data availability. Increased computing power enables the development of sophisticated AI models, surpassing human-level capabilities. Algorithmic innovations, such as neural networks, revolutionize AI applications in various domains. The abundance of data from diverse sources fuels AI growth, empowering decision-making and innovation. AI's transformative potential is evident in multiple sectors and refined enough to be integrated into the economy, solving a broad sepctrum of real use-cases. 
The accelaration, however, is not limited to the most hyped topics, again taking into account the mass of different fields included in or affected by AI.    

While we measured breakthroughs in terms of decades and years, we are currently seeing trends towards breakthroughs on a week to week basis.
This - in addition to the extremely broad field of AI and its asynchronous develeopment - encapsualtes challenges. 
The main hypothesis that the project evolves around, shell propose that the development of robust yet adaptable interfaces as foundational components of digital infrastructure are crucial for creating sustainable and cost-effective solutions while minimizing risks associated with dependency, particularly in conjunction with the accelerating pace of research and development.

# Project Background
In 2015, I started a project around an assistance system. In 2016, it ran on a Raspberry Pi 3 Model B SBC and used [pocketsphinx](https://github.com/cmusphinx/pocketsphinx) in addition to [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus) to allow for dynamically scalable offline speach-to-text transformation. 
In the backend a simple Python script calculated intention scores based on a dictionary of nested tasks and picked, picked the most likely one and tried to extract parameters from the parsed voice command by regular expressions, validation and auto-correcting functionality. At the time, this system was suprisingly stable outside of the parameter extraction and allowed for faster and more pleasant working, espacially in administrative tasks. 
Later iterations with inspiration from the projects [Jasper](https://github.com/jasperproject) and [Naomi](https://github.com/NaomiProject/Naomi) made the project more adaptable by integrating different components (speach-to-text, text-to-speach, intent-calculation, ...) through more robust interfaces which allowed more rapid feature integration but also dynamicly adjusting the used frameworks to task or hardware requirements. 

A large gap in developement followed and today we have access to sophisticated Machine Learning frameworks and models, usable with general hardware.
Therefore this project aims to test different approaches, architectures and tools for optimizing assistance systems with a high focus on interfaces. 

# Scientific Background
While Cognitive Architecture as subfield of Computational Cognition is part of the project name, there is quite a number of fields that play a role in the scientific foundation of the project and that might be more important in the end. Those fields are mostly based in Artificial Intelligence, but not exclusively: 
Robotics, Natural Language Processing and Understanding, Machine Learning, Expert Systems, Knowledge Representation, ...
In an endeavor to not create an opaque mess and cause even more confusion on the not so cleanly defined and bordered topic of AI, I will organize mentioned topics in respect to the project's components for which they are important later on.

# Branches
Work is currently done in "development" branch. Playgrounds for testing are created (and deleted) dynamically.

# Interesting Projects
There are many projects around related ideas and topics. Many of them are not only fun to work with but can also be easily integrated into complex problem solving systems:

- [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui): AUTOMATIC1111's repo sparked my interest which resulted in looking deeper into the collectional topic of Generative AI
- [kohya_ss](https://github.com/bmaltais/kohya_ss): bmaltais' project allowes for easy training of stable-diffusion models and model extensions
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui): Oobabooga's repo follows the example of the stable-diffusion-webui and allows for easy access to the accelerating field of text-generation which itself accelerates the development around this field
- [peft](https://github.com/huggingface/peft): Huggingface's project allows for simple and straightforward finetuning of models
- [privateGPT](https://github.com/imartinez/privateGPT): Imartinez' project is a good example for using [LangChain](https://docs.langchain.com/docs/) and Embeddings/Semantic Search for dynamically adjusting the knowledge base used from and accessible through a language model
- [h2ogpt](https://github.com/h2oai/h2ogpt): H2oai's project seems to aim in a similar direction but I will have to look deeper into it myself
