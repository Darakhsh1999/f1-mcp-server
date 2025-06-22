import numpy as np
import matplotlib as mpl

from PIL import Image
from io import BytesIO
from typing import Union
from fastf1.core import Session
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

# Custom types
gp = Union[str, int]
session_type = Union[str, int, None]


def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)


def create_track_speed_visualization(session: Session) -> Image:

    weekend = session.event
    lap = session.laps.pick_fastest()

    # Get telemetry data
    x = lap.telemetry['X']              # values for x-axis
    y = lap.telemetry['Y']              # values for y-axis
    color = lap.telemetry['Speed']      # value to base color gradient on


    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # We create a plot with title and adjust some setting to make it look good.
    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'[Speed] {weekend["EventName"]} - {lap["Driver"]} #{lap["DriverNumber"]} ', size=24, y=0.97)

    # Adjust margins and turn of axis
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    # After this, we plot the data itself.
    # Create background track line
    ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
            color='black', linestyle='-', linewidth=16, zorder=0)

    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=mpl.colormaps['viridis'], norm=norm,
                        linestyle='-', linewidth=5)

    # Set the values used for colormapping
    lc.set_array(color)

    # Merge all line segments together
    line = ax.add_collection(lc)

    # Finally, we create a color bar as a legend.
    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
    legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=mpl.colormaps['viridis'],
                                    orientation="horizontal")
    legend.set_label("Speed [km/h]")

    # Create a PIL image from the plot
    fig = plt.gcf()
    
    # Save the figure to a BytesIO buffer and convert to bytes
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    # Create PIL image from buffer bytes and close the figure
    img_data = buf.getvalue()
    plt.close(fig)
    buf.close()
    
    # Create new image from the raw bytes
    img = Image.open(BytesIO(img_data))
    return img


def create_track_corners_visualization(session: Session) -> Image:
    
    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()

    circuit_info = session.get_circuit_info()


    # Get an array of shape [n, 2] where n is the number of points and the second
    # axis is x and y.
    track = pos.loc[:, ('X', 'Y')].to_numpy()

    # Convert the rotation angle from degrees to radian.
    track_angle = circuit_info.rotation / 180 * np.pi

    # Rotate and plot the track map.
    rotated_track = rotate(track, angle=track_angle)
    plt.plot(rotated_track[:, 0], rotated_track[:, 1])

    offset_vector = [500, 0]  # offset length is chosen arbitrarily to 'look good'

    # Iterate over all corners.
    for _, corner in circuit_info.corners.iterrows():
        # Create a string from corner number and letter
        txt = f"{corner['Number']}{corner['Letter']}"

        # Convert the angle from degrees to radian.
        offset_angle = corner['Angle'] / 180 * np.pi

        # Rotate the offset vector so that it points sideways from the track.
        offset_x, offset_y = rotate(offset_vector, angle=offset_angle)

        # Add the offset to the position of the corner
        text_x = corner['X'] + offset_x
        text_y = corner['Y'] + offset_y

        # Rotate the text position equivalently to the rest of the track map
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)

        # Rotate the center of the corner equivalently to the rest of the track map
        track_x, track_y = rotate([corner['X'], corner['Y']], angle=track_angle)

        # Draw a circle next to the track.
        plt.scatter(text_x, text_y, color='grey', s=140)

        # Draw a line from the track to this circle.
        plt.plot([track_x, text_x], [track_y, text_y], color='grey')

        # Finally, print the corner number inside the circle.
        plt.text(text_x, text_y, txt,
                va='center_baseline', ha='center', size='small', color='white')


    plt.title(session.event['Location'])
    plt.xticks([])
    plt.yticks([])
    plt.axis('equal')
    
    # Create a PIL image from the plot
    fig = plt.gcf()
    
    # Save the figure to a BytesIO buffer and convert to bytes
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    # Create PIL image from buffer bytes and close the figure
    img_data = buf.getvalue()
    plt.close(fig)
    buf.close()
    
    # Create new image from the raw bytes
    img = Image.open(BytesIO(img_data))
    return img


def create_track_gear_visualization(session: Session) -> Image:
    weekend = session.event
    lap = session.laps.pick_fastest()
    tel = lap.get_telemetry()

    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    gear = tel['nGear'].to_numpy().astype(float)

    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
    fig.suptitle(f'[Gear] {weekend["EventName"]} - {lap["Driver"]} #{lap["DriverNumber"]}', size=24, x=0.5, ha='center', y=0.97)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
    ax.axis('off')

    # Plot a background track line (black, thick) for context
    ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
            color='black', linestyle='-', linewidth=16, zorder=0)

    # Draw the colored segments
    lc_comp = LineCollection(segments, norm=plt.Normalize(gear.min(), gear.max()), cmap=plt.cm.get_cmap('viridis', 8))
    lc_comp.set_array(gear)
    lc_comp.set_linewidth(4)
    ax.add_collection(lc_comp)

    # Set axis limits to the data range with padding to avoid clipping
    x_pad = (x.max() - x.min()) * 0.03
    y_pad = (y.max() - y.min()) * 0.03
    ax.set_xlim(x.min() - x_pad, x.max() + x_pad)
    ax.set_ylim(y.min() - y_pad, y.max() + y_pad)

    # Set axis equal for correct aspect
    ax.set_aspect('equal', adjustable='datalim')

    # Add colorbar at the bottom
    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
    normlegend = plt.Normalize(1, 8)
    legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=plt.cm.get_cmap('viridis', 8),
                                       orientation="horizontal")
    legend.set_ticks(np.arange(1, 9))
    legend.set_ticklabels(np.arange(1, 9))
    legend.set_label("Gear")

    # Create a PIL image from the plot
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_data = buf.getvalue()
    plt.close(fig)
    buf.close()
    img = Image.open(BytesIO(img_data))
    return img
    