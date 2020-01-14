import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='emora_stdm',
     version='1.0',
     scripts=[],
     author="James Finch",
     author_email="jdfinch@emory.edu",
     description="Library for creating state-machine-based chatbots.",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/emora-chat/EmoraSTDM.git",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )