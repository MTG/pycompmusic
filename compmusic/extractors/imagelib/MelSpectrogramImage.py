'''
Created on Nov 2, 2016

@author: georgid
'''
from compmusic.extractors.imagelib.processing import SpectrogramImage,\
    AudioProcessor, WaveformImage
import numpy as np
import essentia.standard as ess
import essentia


class MelSpectrogramImage(SpectrogramImage):
    '''
    Mel Spectrogram as a special case of Spectrogram with fewer spectral bins 
    redefines the ``y_to_bin``
    to be up until number of  mel-scale bands 
    

    '''
    
    def __init__(self, image_width, image_height,  scale_exp, pallete, num_mel_bands):
        f_min=0; f_max=0; fft_size = 0 # dummy becasue spectrogram computation done within MFCC in essentia 
        SpectrogramImage.__init__(self, image_width, image_height, fft_size, f_min, f_max, scale_exp, pallete)
        
        
         # generate the lookup which translates y-coordinate to mel-spectrum-bin
        self.y_to_bin = []
        
        band_bins = np.linspace(0, num_mel_bands, image_height) # num_mel_bands-1 is a workaround because index + 1 is called in compmusic.extractors.imagelib.processing.SpectrogramImage.draw_spectrum
        for i,y in enumerate(range(self.image_height)):
            bin = band_bins[i] 
            if bin < num_mel_bands - 1:
                alpha = bin - int(bin)
                
                self.y_to_bin.append((int(bin), alpha * 255))

class InvMFCCAudioProcessor(AudioProcessor):
    '''
    Compute melbands by inversing the dct of mfcc.
    Use to visualize mfcc in spectral domain for Lyrics-to-audio alignment: (compmusic.extractors.makam.lyricsalign) 
    Emulates the MFCCs extracted with htk, except for hopsize, depending on logic in
    compmusic.extractors.imagelib.MelSpectrogramImage.create_wave_images
    ( see explanation in class PitchExtract Found at: compmusic.extractors.pitch )
    '''
    NUM_MFCC_COEFFS = 13    
    
    def __init__(self, input_filename, fft_size, numMelBands):
        fft_size_dummy = 1024
        window_function_dummy = np.hanning
        AudioProcessor.__init__(self, input_filename, fft_size_dummy, window_function_dummy)

#             self.inv_mfcc_transform = InvMFCC() # inverse mfcc transform
#             self.inv_mfcc_transform.setup()
        self.framesize = 1102 #  default frame size in htk, at rate of 44100
        zeroPadding = fft_size - self.framesize
        self.w = ess.Windowing(type = 'hamming', 
                    size = self.framesize, 
                    zeroPadding = zeroPadding,
                    normalized = False,
                    zeroPhase = False)
        
        spectrumSize= fft_size//2+1
        self.spectrum = ess.Spectrum(size = fft_size)
        self.mfcc = ess.MFCC(inputSize = spectrumSize, # htk-like  mfccs
                    type = 'magnitude', 
                    warpingFormula = 'htkMel',
                    weighting = 'linear',
                    highFrequencyBound = 8000,
                    lowFrequencyBound = 0,
                    numberBands = numMelBands,
                    numberCoefficients = 13,
                    normalize = 'unit_max',
                    dctType = 3,
                    logType = 'log',
                    liftering = 22)

        self.idct = ess.IDCT(inputSize = InvMFCCAudioProcessor.NUM_MFCC_COEFFS, 
                outputSize=numMelBands, 
                dctType = 3, 
                liftering = 22)
        

    def compute_inv_mfcc(self, seek_point, spec_range = 110):
        '''
        Compute the inverse DCT of MFCC for one frame. 
        
        Parameters
        ----------
        seek_point : int
            index of audio sample, around which window is centered 
        spec_range : int 
            min decibel from which scaling is done
        
        Returns 
        -------------------------------
        mel_spectrum : array of float32
            the inverted mfcc to mel spectrum  
        
        '''
        samples_frame = self.read(seek_point - self.framesize/2, self.framesize, True)

        samples_frame = essentia.array(samples_frame)
        
        
#         mfcc_bands, mfcc_coeffs = self.inv_mfcc_transform.frame_to_mfcc(samples_frame)
#         inv_mfccs_spectrum = np.dot(self.inv_mfcc_transform.inv_DCT, mfcc_coeffs[1:])
        
        ### PROBLEM: the range of inv_mfccs_spectrum is -70 to 60, it should be in db.
#         inv_mfccs_spectrum -= np.max(inv_mfccs_spectrum)
        
       
        spect = self.spectrum(self.w(samples_frame))

        mfcc_bands, mfcc_coeffs = self.mfcc(spect)
        mel_bands = np.exp(self.idct(mfcc_coeffs))
        
#         db_inv_mfcc_spectrum = ((inv_mfccs_spectrum).clip(-spec_range, 0.0) + spec_range) /spec_range
        db_mel_bands =   ((20*(np.log10(mel_bands + 1e-60))).clip(-spec_range, 0.0) + spec_range)/spec_range # db  and scale from [- range db ... 0 db] > [0..1] 

        return db_mel_bands

def create_wave_images(input_filename, output_filename_w, output_filename_s, output_filename_m, image_width, image_height, fft_size, progress_callback=None, f_min=None, f_max=None, scale_exp=None, pallete=None):
    """
    Utility function for creating both wavefile and spectrum images from an audio input file.
    """
    numMelBands=26 # as in htk
    processor = AudioProcessor(input_filename, fft_size, np.hanning)
    inv_processor = InvMFCCAudioProcessor(input_filename, fft_size, numMelBands)
    samples_per_pixel = processor.audio_file.nframes / float(image_width)

    waveform = WaveformImage(image_width, image_height)
    spectrogram = SpectrogramImage(image_width, image_height, fft_size, f_min, f_max, scale_exp, pallete)
    mel_spectrogram = MelSpectrogramImage(image_width, image_height, scale_exp, pallete, numMelBands)
    
    for x in range(image_width):

        if image_width >= 10:
            if progress_callback and x % (image_width/10) == 0:
                progress_callback((x*100)/image_width)

        seek_point = int(x * samples_per_pixel)
        next_seek_point = int((x + 1) * samples_per_pixel)

        (spectral_centroid, db_spectrum) = processor.spectral_centroid(seek_point)
        peaks = processor.peaks(seek_point, next_seek_point)

        inv_mfcc_spectrum = inv_processor.compute_inv_mfcc(seek_point) # inv MFCC computation results in a mel spectrogram

        waveform.draw_peaks(x, peaks, spectral_centroid)
        spectrogram.draw_spectrum(x, db_spectrum) 
        mel_spectrogram.draw_spectrum(x, inv_mfcc_spectrum)

    if progress_callback:
        progress_callback(100)

    waveform.save(output_filename_w)
    spectrogram.save(output_filename_s)
    mel_spectrogram.save(output_filename_m)


