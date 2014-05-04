# configurations.py

'''
Todo 
max_sensor_df_value

is this done?
base_noise_threshold 

'''


# Universal:
com='/dev/cu.usbserial-AE00FRN7'
# com='COM3'
threshold_max_ratio = 10 #compute_location
baudrate = 115200

# Posterboard
connectioncmd='ATDMLE,ECFE7E1067AC\r\n' # posterboard command
f_LO = 4650000
factor = 2
valid_channels = [0,1,2,3,4,5,7]
num_channels = len(valid_channels)
pt_num_samples_to_use = 5
max_sum_value = 12000
hor_channels = [1,2,3,4]
vert_channels = [7,6,5]
threshold_channel_zdir = [150,100,100,200,250,250,100]
threshold_ratio_hor = 10
threshold_ratio_vert = 10
threshold_ratio = 10
base_noise_threshold = 150
max_sensor_df_value = 2000


# ITO Display
# f_LO = 4650000
# factor = 16
# valid_channels = [0,1,2,4,5,6,7]
# num_channels = len(valid_channels)
# pt_num_samples_to_use = 5
# max_sum_value = 12000
# hor_channels = [7,3,2,1]
# vert_channels = [4,5,6]
# threshold_channel_zdir = [150,100,100,200,250,250,100]
# threshold_ratio_hor = 9
# threshold_ratio_vert = 12
# threshold_ratio = 10
# base_noise_threshold = 350
# max_sensor_df_value = 2000


# trackpad



# cursor demo
possible_screens = [(800,400), (1440,900), (1920,1080)]
screen_size = possible_screens[0]
z_pos_limit = .08






