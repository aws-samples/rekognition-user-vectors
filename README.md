## Improving Accuracy of Rekognition Face Search with User Vectors
### Face matching of images against a private collection of users faces
![results](./results.jpeg)

---
This repository contains an end to end example (implemented in a Jupyter notebook) how to build a face matching system using [Amazon Rekognition](https://aws.amazon.com/rekognition/). The idea is building a face matching workflow that is capable of matching faces based on multiple images representing their facial features.<br>
The solution contain detailed example of how to create collection, add users, add faces from images, associate faces with users and lastly match faces from images against the user collection.

In Jun 2023, [AWS launched a new capability that significantly improves face search accuracy](https://aws.amazon.com/about-aws/whats-new/2023/06/amazon-rekognition-face-search-accuracy-user-vectors/) by leveraging multiple face images of a user. Now, customers can create User Vectors, which aggregate multiple face vectors of the same user. User vectors offer higher face search accuracy with more robust depictions, as they contain varying degrees of lighting, sharpness, pose, appearance, etc; Thus improving the accuracy when comparing to a facial vector from the image you wish to compare to the collection. 

**NOTE: You can run the notebook in SageMaker Studio, JupyterLab, or on your local machine**

---

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

