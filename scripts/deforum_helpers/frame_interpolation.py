import os
from pathlib import Path
from rife.inference_video import run_rife_new_video_infer
from .video_audio_utilities import get_quick_vid_info, vid2frames, media_file_has_audio, extract_number, ffmpeg_stitch_video
from film_interpolation.film_inference import run_film_interp_infer
from .general_utils import duplicate_pngs_from_folder, checksum

# gets 'RIFE v4.3', returns: 'RIFE43'   
def extract_rife_name(string):
    parts = string.split()
    if len(parts) != 2 or parts[0] != "RIFE" or (parts[1][0] != "v" or not parts[1][1:].replace('.','').isdigit()):
        raise ValueError("Input string should contain exactly 2 words, first word should be 'RIFE' and second word should start with 'v' followed by 2 numbers")
    return "RIFE"+parts[1][1:].replace('.','')

# This function usually gets a filename, and converts it to a legal linux/windows *folder* name
def clean_folder_name(string):
    illegal_chars = ["/", "\\", "<", ">", ":", "\"", "|", "?", "*", "."]
    for char in illegal_chars:
        string = string.replace(char, "_")
    return string

def set_interp_out_fps(interp_x, slow_x_enabled, slom_x, in_vid_fps):
    if interp_x == 'Disabled' or in_vid_fps in ('---', None, '', 'None'):
        return '---'

    # clean_interp_x = extract_number(interp_x)
    # clean_slom_x = extract_number(slom_x)
    fps = float(in_vid_fps) * int(interp_x)
    # if slom_x != -1:
    if slow_x_enabled:
        fps /= int(slom_x)
    return int(fps) if fps.is_integer() else fps
    
# get uploaded video frame count, fps, and return 3 valuees for the gradio UI: in fcount, in fps, out fps (using the set_interp_out_fps function above)
def gradio_f_interp_get_fps_and_fcount(vid_path, interp_x, slow_x_enabled, slom_x):
    if vid_path is None:
        return '---', '---', '---'
    fps, fcount, resolution = get_quick_vid_info(vid_path.name)
    expected_out_fps = set_interp_out_fps(interp_x, slow_x_enabled, slom_x, fps)
    return (fps if fps is not None else '---', fcount if fcount is not None else '---', expected_out_fps)

# handle call to interpolate an uploaded video from gradio button in args.py (the function that calls this func is named 'upload_vid_to_rife')
def process_interp_vid_upload_logic(file, engine, x_am, sl_enabled, sl_am, keep_imgs, f_location, f_crf, f_preset, in_vid_fps, f_models_path, vid_file_name):

    print("got a request to *frame interpolate* an existing video.")

    _, _, resolution = get_quick_vid_info(file.name)
    folder_name = clean_folder_name(Path(vid_file_name).stem)
    outdir_no_tmp = os.path.join(os.getcwd(), 'outputs', 'frame-interpolation', folder_name)
    i = 1
    while os.path.exists(outdir_no_tmp):
        outdir_no_tmp = os.path.join(os.getcwd(), 'outputs', 'frame-interpolation', folder_name + '_' + str(i))
        i += 1

    outdir = os.path.join(outdir_no_tmp, 'tmp_input_frames')
    os.makedirs(outdir, exist_ok=True)
    
    vid2frames(video_path=file.name, video_in_frame_path=outdir, overwrite=True, extract_from_frame=0, extract_to_frame=-1, numeric_files_output=True, out_img_format='png')
    
    # check if the uploaded vid has an audio stream. If it doesn't, set audio param to None so that ffmpeg won't try to add non-existing audio to final video.
    audio_file_to_pass = None
    if media_file_has_audio(file.name, f_location):
        audio_file_to_pass = file.name
    
    process_video_interpolation(frame_interpolation_engine=engine, frame_interpolation_x_amount=x_am, frame_interpolation_slow_mo_enabled = sl_enabled,frame_interpolation_slow_mo_amount=sl_am, orig_vid_fps=in_vid_fps, deforum_models_path=f_models_path, real_audio_track=audio_file_to_pass, raw_output_imgs_path=outdir, img_batch_id=None, ffmpeg_location=f_location, ffmpeg_crf=f_crf, ffmpeg_preset=f_preset, keep_interp_imgs=keep_imgs, orig_vid_name=folder_name, resolution=resolution)

# handle params before talking with the actual interpolation module (rifee/film, more to be added)
def process_video_interpolation(frame_interpolation_engine, frame_interpolation_x_amount, frame_interpolation_slow_mo_enabled, frame_interpolation_slow_mo_amount, orig_vid_fps, deforum_models_path, real_audio_track, raw_output_imgs_path, img_batch_id, ffmpeg_location, ffmpeg_crf, ffmpeg_preset, keep_interp_imgs, orig_vid_name, resolution):

     # set initial output vid fps
    fps = float(orig_vid_fps) * frame_interpolation_x_amount
    
    # re-calculate fps param to pass if slow_mo mode is enabled
    if frame_interpolation_slow_mo_enabled:
        fps = float(orig_vid_fps) * frame_interpolation_x_amount / int(frame_interpolation_slow_mo_amount)

    if frame_interpolation_engine == 'None':
        return
    elif frame_interpolation_engine.startswith("RIFE"):
        # make sure interp_x is valid and in range
        if frame_interpolation_x_amount not in range(2, 11):
            raise Error("frame_interpolation_x_amount must be between 2x and 10x")

        # disable audio-adding by setting real_audio_track to None if slow-mo is enabled (not equal to -1 means enabled)
        if real_audio_track is not None and frame_interpolation_slow_mo_amount != -1:
            real_audio_track = None    
            
        # set UHD to True if res' is 2K or higher
        if resolution:
            UHD = resolution[0] >= 2048 and resolution[1] >= 2048
        else:
            UHD = False
        # e.g from "RIFE v2.3 to RIFE23"
        actual_model_folder_name = extract_rife_name(frame_interpolation_engine)
        
        # run actual rife interpolation and video stitching etc - the whole suite
        run_rife_new_video_infer(interp_x_amount=frame_interpolation_x_amount, slow_mo_enabled = frame_interpolation_slow_mo_enabled, slow_mo_x_amount=frame_interpolation_slow_mo_amount, model=actual_model_folder_name, fps=fps, deforum_models_path=deforum_models_path, audio_track=real_audio_track, raw_output_imgs_path=raw_output_imgs_path, img_batch_id=img_batch_id, ffmpeg_location=ffmpeg_location, ffmpeg_crf=ffmpeg_crf, ffmpeg_preset=ffmpeg_preset, keep_imgs=keep_interp_imgs, orig_vid_name=orig_vid_name, UHD=UHD)
    elif frame_interpolation_engine == 'FILM':
        prepare_film_inference(deforum_models_path=deforum_models_path, x_am=frame_interpolation_x_amount, sl_enabled=frame_interpolation_slow_mo_enabled, sl_am=frame_interpolation_slow_mo_amount, keep_imgs=keep_interp_imgs, raw_output_imgs_path=raw_output_imgs_path, img_batch_id=img_batch_id, f_location=ffmpeg_location, f_crf=ffmpeg_crf, f_preset=ffmpeg_preset, fps = fps)
    else:
        print("Unknown Frame Interpolation engine chosen. Doing nothing.")
        return
        
def prepare_film_inference(deforum_models_path, x_am, sl_enabled, sl_am, keep_imgs, raw_output_imgs_path, img_batch_id, f_location, f_crf, f_preset, fps):
    import shutil 
    
    film_model_name = 'film_net_fp16.pt'
    film_model_folder = os.path.join(deforum_models_path,'film_interpolation')
    film_model_path = os.path.join(film_model_folder, film_model_name)
    final_output_interp_imgs_folder = os.path.join(raw_output_imgs_path, 'interpolated_frames_film_' + str(img_batch_id))
    interp_vid_path = os.path.join(raw_output_imgs_path, str(img_batch_id) + '_FILM_x' + str(x_am))
    img_path_for_ffmpeg = os.path.join(final_output_interp_imgs_folder, "frame_%05d.png")

    if sl_enabled:
        interp_vid_path = interp_vid_path + '_slomo_x' + str(sl_am)
    interp_vid_path = interp_vid_path + '.mp4'

     # In this folder we temporarily keep the original frames (converted/ copy-pasted and img format depends on scenario)
    # the convertion case is done to avert a problem with 24 and 32 mixed outputs from the same animation run
    temp_convert_raw_png_path = os.path.join(raw_output_imgs_path, "tmp_film_folder")
    total_frames = duplicate_pngs_from_folder(raw_output_imgs_path, temp_convert_raw_png_path, img_batch_id, None)
    check_and_download_film_model('film_net_fp16.pt', os.path.join(deforum_models_path, 'film_interpolation')) # TODO: split this part
    
    # get number of in-between-frames to provide to FILM - mimics how RIFE works, we should get the same amount of total frames in the end
    film_in_between_frames_count = calculate_frames_to_add(total_frames, x_am)
    
    run_film_interp_infer(
    model_path = film_model_path,
    input_folder = temp_convert_raw_png_path,
    save_folder = final_output_interp_imgs_folder,
    inter_frames = film_in_between_frames_count)
    
    # TODO:  HANDLE AUDIO?!
    print (f"*Passing interpolated frames to ffmpeg...*")
    exception_raised = False
    try:
        ffmpeg_stitch_video(ffmpeg_location=f_location, fps=fps, outmp4_path=interp_vid_path, stitch_from_frame=0, stitch_to_frame=999999, imgs_path=img_path_for_ffmpeg, add_soundtrack='None', audio_path=None, crf=f_crf, preset=f_preset)
    except Exception as e:
        exception_raised = True
        print(f"An error occurred while stitching the video: {e}")

    # delete interp frames only if there was no error in the ffmpeg step and keep_imgs is False
    if not keep_imgs and not exception_raised:
        try:
            shutil.rmtree(final_output_interp_imgs_folder)
        except:
            pass
    try: # delete duplicated raw non-interpolated frames
        shutil.rmtree(temp_convert_raw_png_path)
    except:
        pass
    
def check_and_download_film_model(model_name, model_dest_folder):
    from basicsr.utils.download_util import load_file_from_url
    if model_name == 'film_net_fp16.pt':
        model_dest_path = os.path.join(model_dest_folder, model_name)
        download_url = 'https://github.com/hithereai/frame-interpolation-pytorch/releases/download/film_net_fp16.pt/film_net_fp16.pt'
        film_model_hash = '0a823815b111488ac2b7dd7fe6acdd25d35a22b703e8253587764cf1ee3f8f93676d24154d9536d2ce5bc3b2f102fb36dfe0ca230dfbe289d5cd7bde5a34ec12'
    else: # Unknown FILM model
        raise Exception("Got a request to download an unknown FILM model. Can't proceed.")
    if os.path.exists(model_dest_path):
        return
    try:
        os.makedirs(model_dest_folder, exist_ok=True)
        # download film model from url
        load_file_from_url(download_url, model_dest_folder)
        # verify checksum
        if checksum(model_dest_path) != film_model_hash:
            raise Exception(f"Error while downloading {model_name}. Please download from: {download_url}, and put in: {model_dest_folder}")
    except Exception as e:
        raise Exception(f"Error while downloading {model_name}. Please download from: {download_url}, and put in: {model_dest_folder}")
        
def calculate_frames_to_add(n, x):
    frames_to_add = (n * x - n) / (n - 1)
    return int(round(frames_to_add))