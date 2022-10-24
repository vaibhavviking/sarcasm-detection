import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import numpy as np
import os
import pickle
from tqdm import tqdm
from transformers import ViTFeatureExtractor, ViTModel


model = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224-in21k")
# model.to(DEVICE)

transf = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_frames(frames_folder_path):
	# Get all frame file names
  frames = []

  frames_file = os.listdir(frames_folder_path)

  for i,frame_file_name in enumerate(frames_file):
    frame = Image.open(os.path.join(frames_folder_path, frame_file_name))
    frames.append(frame)
    # frame = transf(frame)

    # if frames is None:
    #   frames = torch.empty((len(frames_file), *frame.size()))
    # frames[i] = frame

  return frames


def frames_features(frames_folder_path):
  frames = get_frames(frames_folder_path)
  # frames = frames.to(DEVICE)
  # frames = frames.to(DEVICE)
  # Run the model on input data
  output = []
  batch_size = 32              # 10 for PC
  for start_index in range(0, len(frames),batch_size):
    end_index = min(start_index + batch_size, len(frames))
    frame_range = range(start_index, end_index)
    frame_batch = np.array(frames)[frame_range]
    # frame_batch.to(DEVICE)
    inputs = feature_extractor(list(frame_batch),return_tensors='pt')
    # inputs.to(DEVICE)
    avg_pool_value = model(**inputs)
    # frame_batch.to('cpu')
    output.append(avg_pool_value)

#  output = np.concatenate(output)

  return output

features = {}

def videos_features(frames_folders_path, save_path):
  # frames_folders_path: path to all video frames folders
  # video_path: path ot original videos
  # n_folder = len(os.listdir(frames_folders_path))
  frames_folders = os.listdir(frames_folders_path)
  for frames_folder in tqdm(frames_folders, ncols=100, ascii=True):
    video_feature = {}
#    video_name = os.path.join(videos_path, frames_folder + '.mp4')
    frames_folder_path = os.path.join(frames_folders_path, frames_folder)
    # cam = cv2.VideoCapture(video_name)
    # fps = round(cam.get(cv2.CAP_PROP_FPS), 0)
    feat = frames_features(frames_folder_path)
    # video_feature['fps'] = fps
    # video_feature['resnet152'] = feat
    features[frames_folder] = feat
    #print("Process video {} FPS {} shape {}".format(frames_folder, fps, feat.shape))
    f = open(save_path,'wb')
    pickle.dump(features, f)


def main():
	frames_folders_path = "/frames/utterances_final/"
#	videos_path = "/content/drive/MyDrive/mmsd_raw_data/utterances_final"
	videos_features(frames_folders_path, '/hugging_face_vit_features.pkl')


if __name__ == '__main__':
	main()
