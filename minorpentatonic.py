# Program to generate the sounds of notes of a minor pentatonic scale matching the frequencies of notes in piano

# Import required packages
import numpy as np
import pyaudio
import time
import pandas as pd
import ezodf

# Open open office calc file containing piano note frequencies into a variable
doc = ezodf.opendoc('piano_notes.ods')
print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
for sheet in doc.sheets:
    print("-"*40)
    print("   Sheet name : '%s'" % sheet.name)
    print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )

# convert the first sheet to a pandas.DataFrame
sheet = doc.sheets[0]
df_dict = {}
for i, row in enumerate(sheet.rows()):
    # row is a list of cells
    # assume the header is on the first row
    if i == 0:
        # columns as lists in a dictionary
        df_dict = {cell.value:[] for cell in row}
        # create index for the column headers
        col_index = {j:cell.value for j, cell in enumerate(row)}
        continue
    for j, cell in enumerate(row):
        # use header instead of column index
        df_dict[col_index[j]].append(cell.value)


# and convert to a DataFrame
pianonotes_df = pd.DataFrame(df_dict)


# Create a new column with index values
pianonotes_df['index_column'] = pianonotes_df.index

# Using reset_index() to set index into column
notes_df=pianonotes_df.reset_index()

# drop column which are not required
notes_df.drop('index_column', axis=1, inplace=True)

# Drop all rows with NaN values
pnotes_df=notes_df.dropna()
pnotes_df=notes_df.dropna(axis=0)

# Reset index after drop
pnotes_df=notes_df.dropna().reset_index(drop=True)


# Set sample rate either to 44100 or 48000
SAMPLE_RATE = 44100


def generate_sample(freq, duration, volume):

    amplitude = 2000
    total_samples = np.round(SAMPLE_RATE * duration)
    w = 2.0 * np.pi * freq / SAMPLE_RATE
    k = np.arange(0, total_samples)

    return np.round(amplitude * np.sin(k * w))

# Function to load notes into a list object
def load_notes(notestep, notestep1, notescale):
    
    # Interval of notes for a minor pentatonic scale
    notes_interval = [3, 2, 2, 3, 2, 2]
    rev_interval = [0, 2, 3, 2, 2, 3]
    tones_fwd, tones_rev = [], []
    
    print(f'The frequencies of notes in the {notescale} minor pentatonic scale in ascending order')
    for note in notes_interval: 
        # print the frequency ascending notes of the scale        
        print(rev_freq[notestep])
        
        # Call function to generate the equivalent tone for the given frequency
        tone = np.array(generate_sample(rev_freq[notestep], 1, 1.0), dtype=np.int16)    
        notestep = note + notestep

        # Appending the ascending tones of the scale to a list
        tones_fwd.append(tone)
    
    print()
    print(f'The frequencies of notes in the {notescale} minor pentatonic scale in descending order')

    for note in rev_interval: 
        notestep1 = notestep1 - note
        # Call function to generate the equivalent tone for the given frequency
        tone1 = np.array(generate_sample(rev_freq[notestep1], 1, 1.0), dtype=np.int16) 

        # Appending the descending tones of the scale to a list
        tones_rev.append(tone1)

        # print the frequency descending notes of the scale        
        print(rev_freq[notestep1])

    # Return list of frequencies in the ascending and descending notes of the minor pentatonic scale    
    return tones_fwd, tones_rev


# Function to play the sounds from the generated tones
def fmain(tones_fwd, tones_rev):
    # Instantiate PyAudio and initialize PortAudio system resources
    p = pyaudio.PyAudio()

    # Open stream 
    stream = p.open(format=p.get_format_from_width(width=2), 
                    channels=2, 
                    rate=SAMPLE_RATE,
                    output=True)
 

    # Play samples from the tones list with a interval between successive notes
    # This list is the ascending order. That is from lower to higher frequency octave
    for tone in tones_fwd:
        stream.write(tone)
        time.sleep(0.0005) # wait for 0.5 milli seconds between tones

    # Play samples from the tones1 list with a interval between successive notes
    # This list is the descending order. That is from higher to lower frequency octave
    for tone1 in tones_rev:
        stream.write(tone1)
        time.sleep(0.0005) # wait for 0.5 milli seconds between tones
        
    stream.stop_stream()
    # Close stream 
    stream.close()
    
    # Release PortAudio system resources 
    p.terminate()


# Function to locate the rows and columbs in the dataframe for the given notes in the scale list
def locate_in_df(pnotes_df, value):
    a = pnotes_df.to_numpy()
    row = np.where(a == value)[0][0]
    col = np.where(a == value)[1][0]
    return row, col

# Scale list for which the minor pentatonic scale will be played in sequence
scale_list = ['C4', 'G4', 'F4', 'E4', 'C5']

notestep = 0
notestep1 = 12

# Function to play the scales for the given notes in the scale list
for notescale in scale_list:
    row, col= locate_in_df(pnotes_df, notescale)
    print('___________')
    # Position of note in the dataframe
    #print(f"Row : {row} and column : {col}  of note {notescale} in the data frame pnotes_df")    
                    
    # Use the where method to select rows where index >= selected row
    df_filtered = pnotes_df.where(pnotes_df['index'] <= row).dropna()

    notelist = df_filtered['FrequencyHz'].values.tolist()

    rev_freq = notelist[::-1] 

    tones_fwd, tones_rev = load_notes(notestep, notestep1, notescale)

    # Calling function to play the frequencies converted into tones 
    fmain(tones_fwd, tones_rev)