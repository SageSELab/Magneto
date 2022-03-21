#!/usr/bin/env python
# coding: utf-8

# In[1]:


# get_ipython().run_line_magic('matplotlib', 'inline')
# get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")

# import matplotlib.pyplot as plt

import numpy as np
import torch
import os
from torch import nn
from torch import optim
import torch.nn.functional as F
from torchvision import datasets, transforms, models
from PIL import Image
from torch.autograd import Variable
from binaryClassifier import Net


class ImageFolderWithPaths(datasets.ImageFolder):
    """Custom dataset that includes image file paths. Extends
    torchvision.datasets.ImageFolder
    """

    # override the __getitem__ method. this is the method that dataloader calls
    def __getitem__(self, index):
        # this is what ImageFolder normally returns
        original_tuple = super(ImageFolderWithPaths, self).__getitem__(index)
        # the image file path
        path = self.imgs[index][0]
        # make a new tuple that includes original and the path
        tuple_with_path = original_tuple + (path,)
        return tuple_with_path


classes = ["typing", "noTyping"]

model = Net()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
scriptLocation = os.getcwd()
model_location = os.path.join(scriptLocation,'model_cifar.pt')
checkpoint = torch.load(model_location)

# checkpoint.eval()
model.load_state_dict(checkpoint)
model.eval()
test_transforms = transforms.Compose(
    [transforms.Resize((224, 224)), transforms.ToTensor()]
)


def main():


    # instantiate the dataset and dataloader
    data_dir = "/Users/enter_name/Documents/proj_folder/oracleFromBehavior/backButton/bug_id/result"
    dataset = ImageFolderWithPaths(data_dir, transform=test_transforms)
    # our custom dataset
    dataloader = torch.utils.data.DataLoader(dataset)

    # iterate over data

    for images, labels, paths in dataloader:

        to_pil = transforms.ToPILImage()
        for i in range(len(images)):
            image = to_pil(images[i])
            index = predict_image(image)
            print(paths, ":", "predicted :", str(classes[index]), index)


def predict_image(image):
    image_tensor = test_transforms(image).float()
    image_tensor = image_tensor.unsqueeze_(0)
    input = Variable(image_tensor)
    input = input.to(device)
    output = model(input)
    index = output.data.cpu().numpy().argmax()
    return index


def has_keyboard(img):
    to_pil = transforms.ToPILImage()
    image = to_pil(img)
    index = predict_image(image)
    # print(index, "============")
    return not index  # because 0 == typing and 1 is non typing
