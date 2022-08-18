# Synthesizing Part Span Shroud for Design Optimization using Genetic Algorithm

This repository is the implementation corresponding to the paper "Encoding and Synthesizing Part Span Shroud for Aero-Structural Design Optimization using Genetic Algorithm", linked here.

Our model is built upon VAEGAN, which combines the encoder-decoder architecture from VAE and the discriminator from GAN.
Through this method of dimension reduction, we also study the role of each encoded dimension of the feature domain, which represent geometric information.
Moreover, novel shrouds are synthesized by interpolating and extrapolating learned features from different shrouds, which inherit features from existing shrouds. Also, shrouds can be generated from Gaussian noise, which introduce more novelty.
Finally, the synthesized shrouds can be optimized via GA to possess competitive or even better aero-structural properties in comparison to existing ones. 
The results of this article indicated that autoencoders can be used to perform design optimization with higher accuracy as well as reduce the dimensionality.
