import os

from itertools import chain
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from torch.autograd import Variable
from dataloader import testset_list_classifier ,testset_loader, npyDataset
from train import reparameterize, get_z_random, get_z_random_sparse
from model import Generator, Discriminator, ContentEncoder, StyleEncoder
from matplotlib.pyplot import imsave
from utils import Tanhize 
from hparams import get_hparams


# Save sample image


def test():

    hparams = get_hparams()
    print(hparams.task_name)
    model_path = os.path.join( hparams.model_path, hparams.task_name, hparams.spec_opt )

        
    # Load Dataset Loader


    root = '../dataset/feat/test'
    list_dir_A = './etc/Test_dt05_real_isolated_1ch_track_list.csv'
    list_dir_B = './etc/Test_dt05_simu_isolated_1ch_track_list.csv'

    output_dir = './output/{}/{}_img'.format(hparams.task_name, hparams.iteration_num)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    normalizer_clean = Tanhize('clean')
    normalizer_noisy = Tanhize('noisy')
    test_list_A, speaker_A = testset_list_classifier(root, list_dir_A)
    test_list_B, speaker_B = testset_list_classifier(root, list_dir_B)


    generator_A = Generator()
    generator_B = Generator()
    discriminator_A = Discriminator()
    discriminator_B = Discriminator()
    ContEncoder_A = ContentEncoder()
    ContEncoder_B = ContentEncoder()

    StEncoder_A = StyleEncoder()
    StEncoder_B = StyleEncoder()


    generator_A = nn.DataParallel(generator_A).cuda()
    generator_B = nn.DataParallel(generator_B).cuda()
    discriminator_A = nn.DataParallel(discriminator_A).cuda()
    discriminator_B = nn.DataParallel(discriminator_B).cuda()

    ContEncoder_A = nn.DataParallel(ContEncoder_A).cuda()
    ContEncoder_B = nn.DataParallel(ContEncoder_B).cuda()

    StEncoder_A = nn.DataParallel(StEncoder_A).cuda()
    StEncoder_B = nn.DataParallel(StEncoder_B).cuda()


    map_location = lambda storage, loc: storage
    generator_A.load_state_dict(
        torch.load('./models/{}/{}/model_gen_A_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))
    generator_B.load_state_dict(
        torch.load('./models/{}/{}/model_gen_B_{}.pth'.format(hparams.task_name, hparams.spec_opt,hparams.iteration_num), map_location=map_location))
    discriminator_A.load_state_dict(
        torch.load('./models/{}/{}/model_dis_A_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))
    discriminator_B.load_state_dict(
        torch.load('./models/{}/{}/model_dis_B_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))
    ContEncoder_A.load_state_dict(
        torch.load('./models/{}/{}/model_ContEnc_A_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))
    ContEncoder_B.load_state_dict(
        torch.load('./models/{}/{}/model_ContEnc_B_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))
    StEncoder_A.load_state_dict(
        torch.load('./models/{}/{}/model_StEnc_A_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))
    StEncoder_B.load_state_dict(
        torch.load('./models/{}/{}/model_StEnc_B_{}.pth'.format(hparams.task_name, hparams.spec_opt, hparams.iteration_num), map_location=map_location))


    for i in range(10):

        generator_B.eval()
        ContEncoder_A.eval()
        StEncoder_B.eval()


        feat = testset_loader(root, test_list_A[i],speaker_A, normalizer =normalizer_noisy)

        print(feat['audio_name'])
    
        A_content = Variable(torch.FloatTensor(feat['sp']).unsqueeze(0)).cuda()


        A_cont= ContEncoder_A(A_content)

        z_st = get_z_random_sparse(1, 8, 1)
        st_0 = torch.ones((1,8,1))*2
        
        feature_z = generator_B(A_cont, z_st)
        feature_z = normalizer_noisy.backward_process(feature_z.squeeze().data)
        feature_z = feature_z.squeeze().data.cpu().numpy()

        feature_0 = generator_B(A_cont, st_0)
        feature_0 = normalizer_noisy.backward_process(feature_0.squeeze().data)
        feature_0 = feature_0.squeeze().data.cpu().numpy()
        

        imsave( os.path.join( output_dir, 'z-img-' + feat['audio_name'].split('.')[0]+'.png'), feature_z.transpose(), origin='lower')
        imsave( os.path.join( output_dir, '0-img-' + feat['audio_name'].split('.')[0]+'.png'), feature_0.transpose(), origin='lower')

    for i in range(10):

        generator_B.eval()
        ContEncoder_A.eval()


        feat = testset_loader(root, test_list_B[i],speaker_B, normalizer =normalizer_noisy)
        
        print(feat['audio_name'])
    
        A_content = Variable(torch.FloatTensor(feat['sp']).unsqueeze(0)).cuda()

        A_cont= ContEncoder_A(A_content)


        z_st = get_z_random_sparse(1, 8, 1)
    
        feature_z = generator_B(A_cont, z_st)
        feature_z = normalizer_noisy.backward_process(feature_z.squeeze().data)
        feature_z = feature_z.squeeze().data.cpu().numpy()
        
        imsave( os.path.join( output_dir, 'z-img-' + feat['audio_name'].split('.')[0]+'.png'), feature_z.transpose(), origin='lower')





if __name__ == '__main__':
    test()
