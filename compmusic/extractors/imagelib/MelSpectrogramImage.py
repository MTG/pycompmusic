'''
Created on Nov 2, 2016

@author: georgid
'''
from compmusic.extractors.imagelib.processing import SpectrogramImage,\
    AudioProcessor, WaveformImage
import numpy
import essentia
from compmusic.extractors.invMFCC import InvMFCC

class MelSpectrogramImage(SpectrogramImage):
    '''
    Mel Spectrogram as a special case of Spectrogram with fewer spectral bins 
    redefines the ``y_to_bin``
    to be up until number of  mel-scale bands 
    

    '''
    
    def __init__(self, image_width, image_height,  scale_exp, pallete, num_mel_bands):
        f_min=0; f_max=0; fft_size = 0 # dummy
        SpectrogramImage.__init__(self, image_width, image_height, fft_size, f_min, f_max, scale_exp, pallete)
        
        
         # generate the lookup which translates y-coordinate to mel-spectrum-bin
        self.y_to_bin = []
        
        band_bins = numpy.linspace(0, num_mel_bands, image_height) # num_mel_bands-1 is a workaround because index + 1 is called in compmusic.extractors.imagelib.processing.SpectrogramImage.draw_spectrum
        for i,y in enumerate(range(self.image_height)):
            bin = band_bins[i] 
            if bin < num_mel_bands - 1:
                alpha = bin - int(bin)
                
                self.y_to_bin.append((int(bin), alpha * 255))

class InvMFCCAudioProcessor(AudioProcessor):
        
    def __init__(self, input_filename, fft_size, window_function=numpy.hanning):
            AudioProcessor.__init__(self, input_filename, fft_size, window_function)

            self.inv_mfcc_transform = InvMFCC() # inverse mfcc transform
            self.inv_mfcc_transform.setup()
        


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
            the inverted mfcc to mel spectrum with 26 dimnsions 
        
        '''
        samples_frame = self.read(seek_point - self.inv_mfcc_transform.settings.FrameSize/2, self.inv_mfcc_transform.settings.FrameSize, True)

        samples = essentia.array(samples_frame)
        mfcc_bands, mfcc_coeffs = self.inv_mfcc_transform.frame_to_mfcc(samples)
        inv_mfccs_spectrum = numpy.dot(self.inv_mfcc_transform.inv_DCT, mfcc_coeffs[1:])
        abs_inv_mfcc_spectrum = numpy.abs(inv_mfccs_spectrum) # workaround. not sure why inv DCT gives negative values
        
        # scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
        db_inv_mfcc_spectrum = ((20*(numpy.log10(abs_inv_mfcc_spectrum + 1e-60))).clip(-spec_range, 0.0) + spec_range)/spec_range
        return db_inv_mfcc_spectrum

def create_wave_images(input_filename, output_filename_w, output_filename_s, output_filename_m, image_width, image_height, fft_size, progress_callback=None, f_min=None, f_max=None, scale_exp=None, pallete=None):
    """
    Utility function for creating both wavefile and spectrum images from an audio input file.
    """
    processor = InvMFCCAudioProcessor(input_filename, fft_size, numpy.hanning)
    samples_per_pixel = processor.audio_file.nframes / float(image_width)

    waveform = WaveformImage(image_width, image_height)
    spectrogram = SpectrogramImage(image_width, image_height, fft_size, f_min, f_max, scale_exp, pallete)
    inv_mfcc_spectrogram = MelSpectrogramImage(image_width, image_height, scale_exp, pallete, processor.inv_mfcc_transform.settings.BANDS)
    
    for x in range(image_width):

        if image_width >= 10:
            if progress_callback and x % (image_width/10) == 0:
                progress_callback((x*100)/image_width)

        seek_point = int(x * samples_per_pixel)
        next_seek_point = int((x + 1) * samples_per_pixel)

        (spectral_centroid, db_spectrum) = processor.spectral_centroid(seek_point)
        peaks = processor.peaks(seek_point, next_seek_point)

        inv_mfcc_spectrum = processor.compute_inv_mfcc(seek_point) # inv MFCC computation results in a mel spectrogram

        waveform.draw_peaks(x, peaks, spectral_centroid)
        spectrogram.draw_spectrum(x, db_spectrum) 
        inv_mfcc_spectrogram.draw_spectrum(x, inv_mfcc_spectrum)

    if progress_callback:
        progress_callback(100)

    waveform.save(output_filename_w)
    spectrogram.save(output_filename_s)
    inv_mfcc_spectrogram.save(output_filename_m)


