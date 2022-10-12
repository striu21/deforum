import scripts.deforum.args as deforum_args

import modules.scripts as scripts
import gradio as gr

from modules.processing import Processed
from modules.shared import opts, cmd_opts, state
from types import SimpleNamespace

class Script(scripts.Script):

    def title(self):
        return "Deforum"

    def ui(self, is_img2img):
        da = SimpleNamespace(**deforum_args.DeforumAnimArgs()) #default args
        gr.HTML("<p style=\"font-weight:bold;margin-bottom:0.75em\">Import settings from file</p>")
        with gr.Row():
            override_settings_with_file = gr.Checkbox(label="Override settings", value=False, interactive=True)
            custom_settings_file = gr.Textbox(label="Custom settings file", lines=1, interactive=True)
            
            
        gr.HTML("<p style=\"font-weight:bold;margin-bottom:0.75em\">Animation settings</p>")
        with gr.Row():
            animation_mode = gr.Dropdown(label="animation_mode", choices=['None', '2D', '3D', 'Video Input', 'Interpolation'], value=da.animation_mode, type="index", elem_id="animation_mode", interactive=True)
            max_frames = gr.Number(label="max_frames", value=da.max_frames, interactive=True)
            border = gr.Dropdown(label="border", choices=['replicate', 'wrap'], value=da.border, type="index", elem_id="border", interactive=True)
        
        
        gr.HTML("<p style=\"margin-bottom:0.75em\">Motion parameters:</p>")
        gr.HTML("<p style=\"margin-bottom:0.75em\">2D and 3D settings</p>")
        with gr.Row():
            angle = gr.Textbox(label="angle", lines=1, value = da.angle, interactive=True)
        with gr.Row():
            zoom = gr.Textbox(label="zoom", lines=1, value = da.zoom, interactive=True)
        with gr.Row():
            translation_x = gr.Textbox(label="translation_x", lines=1, value = da.translation_x, interactive=True)
        with gr.Row():
            translation_y = gr.Textbox(label="translation_y", lines=1, value = da.translation_y, interactive=True)
        gr.HTML("<p style=\"margin-bottom:0.75em\">3D settings</p>")
        with gr.Row():
            translation_z = gr.Textbox(label="translation_z", lines=1, value = da.translation_z, interactive=True)
        with gr.Row():
            rotation_3d_x = gr.Textbox(label="rotation_3d_x", lines=1, value = da.rotation_3d_x, interactive=True)
        with gr.Row():
            rotation_3d_y = gr.Textbox(label="rotation_3d_y", lines=1, value = da.rotation_3d_y, interactive=True)
        with gr.Row():
            rotation_3d_z = gr.Textbox(label="rotation_3d_z", lines=1, value = da.rotation_3d_z, interactive=True)
        gr.HTML("<p style=\"margin-bottom:0.75em\">Prespective flip — Low VRAM pseudo-3D mode:</p>")
        with gr.Row():
            flip_2d_perspective = gr.Checkbox(label="flip_2d_perspective", value=da.flip_2d_perspective, interactive=True)
        with gr.Row():
            perspective_flip_theta = gr.Textbox(label="perspective_flip_theta", lines=1, value = da.perspective_flip_theta, interactive=True)
        with gr.Row():
            perspective_flip_phi = gr.Textbox(label="perspective_flip_phi", lines=1, value = da.perspective_flip_phi, interactive=True)
        with gr.Row():
            perspective_flip_gamma = gr.Textbox(label="perspective_flip_gamma", lines=1, value = da.perspective_flip_gamma, interactive=True)
        with gr.Row():
            perspective_flip_fv = gr.Textbox(label="perspective_flip_fv", lines=1, value = da.perspective_flip_fv, interactive=True)
        gr.HTML("<p style=\"margin-bottom:0.75em\">Generation settings:</p>")
        with gr.Row():
            noise_schedule = gr.Textbox(label="noise_schedule", lines=1, value = da.noise_schedule, interactive=True)
        with gr.Row():
            strength_schedule = gr.Textbox(label="strength_schedule", lines=1, value = da.strength_schedule, interactive=True)
        with gr.Row():
            contrast_schedule = gr.Textbox(label="contrast_schedule", lines=1, value = da.contrast_schedule, interactive=True)
#TODO
#        with gr.Row():
#            seed_schedule = gr.Textbox(label="seed_schedule", lines=1, value = da.seed_schedule, interactive=True)
#        with gr.Row():
#            scale_schedule = gr.Textbox(label="scale_schedule", lines=1, value = da.scale_schedule, interactive=True)
        
        gr.HTML("<p style=\"margin-bottom:0.75em\">Coherence:</p>")
        with gr.Row():
            color_coherence = gr.Dropdown(label="color_coherence", choices=['None', 'Match Frame 0 HSV', 'Match Frame 0 LAB', 'Match Frame 0 RGB'], value=da.color_coherence, type="index", elem_id="color_coherence", interactive=True)
            diffusion_cadence = gr.Slider(label="diffusion_cadence", minimum=1, maximum=8, step=1, value=1, interactive=True)
            
        gr.HTML("<p style=\"margin-bottom:0.75em\">3D Depth Warping:</p>")
        with gr.Row():
            use_depth_warping = gr.Checkbox(label="use_depth_warping", value=False, interactive=True)
        with gr.Row():
            midas_weight = gr.Number(label="midas_weight", value=da.midas_weight, interactive=True)
            near_plane = gr.Number(label="near_plane", value=da.near_plane, interactive=True)
            far_plane = gr.Number(label="far_plane", value=da.far_plane, interactive=True)
            fov = gr.Number(label="fov", value=da.fov, interactive=True)
            padding_mode = gr.Dropdown(label="padding_mode", choices=['border', 'reflection', 'zeros'], value=da.padding_mode, type="index", elem_id="padding_mode", interactive=True)
            sampling_mode = gr.Dropdown(label="sampling_mode", choices=['bicubic', 'bilinear', 'nearest'], value=da.sampling_mode, type="index", elem_id="sampling_mode", interactive=True)
            save_depth_maps = gr.Checkbox(label="save_depth_maps", value=da.save_depth_maps, interactive=True)
        
        gr.HTML("<p style=\"margin-bottom:0.75em\">Video Input:</p>")
        with gr.Row():
            video_init_path = gr.Textbox(label="video_init_path", lines=1, value = da.video_init_path, interactive=True)
        with gr.Row():
            extract_nth_frame = gr.Number(label="extract_nth_frame", value=da.extract_nth_frame, interactive=True)
            overwrite_extracted_frames = gr.Checkbox(label="overwrite_extracted_frames", value=False, interactive=True)
            use_mask_video = gr.Checkbox(label="use_mask_video", value=False, interactive=True)
        with gr.Row():
            video_mask_path = gr.Textbox(label="video_mask_path", lines=1, value = da.video_mask_path, interactive=True)
        
        gr.HTML("<p style=\"margin-bottom:0.75em\">Interpolation:</p>")
        with gr.Row():
            interpolate_key_frames = gr.Checkbox(label="interpolate_key_frames", value=da.interpolate_key_frames, interactive=True)
            interpolate_x_frames = gr.Number(label="interpolate_x_frames", value=da.interpolate_x_frames, interactive=True)
        
        gr.HTML("<p style=\"margin-bottom:0.75em\">Resume animation:</p>")
        with gr.Row():
            resume_from_timestring = gr.Checkbox(label="resume_from_timestring", value=da.resume_from_timestring, interactive=True)
            resume_timestring = gr.Textbox(label="resume_timestring", lines=1, value = da.resume_timestring, interactive=True)
            

        return [interpolate_x_frames]


    def run(self, p, interpolate_x_frames):
        print('Hello, deforum!')

        display_result_data = [""]

        return Processed(p, *display_result_data)
    
    