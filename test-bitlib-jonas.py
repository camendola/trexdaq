'''Test the BitScope Library by connecting with the first available device
and performing a capture and dump. Requires BitLib 2.0 and Python Bindings'''

from bitlib import *
import matplotlib.pyplot as plt
import numpy as np

MY_DEVICE = 0 # one open device only
MY_CHANNEL = 0 # channel to capture and display
MY_PROBE_FILE = "" # default probe file if unspecified 
MY_MODE = BL_MODE_DUAL # preferred capture mode
MY_RATE = 1000000 # default sample rate we'll use for capture.
MY_SIZE = 5000 # number of samples we'll capture (simply a connectivity test)
TRUE = 1

MODES = ("FAST","DUAL","MIXED","LOGIC","STREAM")
SOURCES = ("POD","BNC","X10","X20","X50","ALT","GND")

def main(argv=None):
    #
    # Open the first device found (only)
    #
    print "Starting: Attempting to open one device..."
    if BL_Open(MY_PROBE_FILE,1):
        #
        # Open succeeded (report versions).
        #
        print " Library: %s (%s)" % (
            BL_Version(BL_VERSION_LIBRARY),
            BL_Version(BL_VERSION_BINDING))
        #
        # Select this device (optional, it's already selected).
        #
        BL_Select(BL_SELECT_DEVICE,MY_DEVICE)
        #
        # Report the link, device and channel information.
        #
        print "    Link: %s" % BL_Name(0)
        print "BitScope: %s (%s)" % (BL_Version(BL_VERSION_DEVICE),BL_ID())
        print "Channels: %d (%d analog + %d logic)" % (
            BL_Count(BL_COUNT_ANALOG)+BL_Count(BL_COUNT_LOGIC),
            BL_Count(BL_COUNT_ANALOG),BL_Count(BL_COUNT_LOGIC))
        #
        # Determine which modes the device supports.
        #
        print "   Modes:" + "".join(["%s" % (
            (" " + MODES[i]) if i == BL_Mode(i) else "") for i in range(len(MODES))])
        #
        # Report canonic capture specification in LOGIC (if supported) or FAST mode (otherwise.
        #
        BL_Mode(BL_MODE_LOGIC) == BL_MODE_LOGIC or BL_Mode(BL_MODE_FAST)
        print " Capture: %d @ %.0fHz = %fs (%s)" % (
            BL_Size(),BL_Rate(),
            BL_Time(),MODES[BL_Mode()])
        #
        # Report the maximum offset range (if the device supports offsets).
        #
        BL_Range(BL_Count(BL_COUNT_RANGE));
        if BL_Offset(-1000) != BL_Offset(1000):
            print "  Offset: %+.4gV to %+.4gV" % (
                BL_Offset(1000), BL_Offset(-1000))
        #
        # Report the input source provided by the device and their respective ranges.
        #
        for i in range(len(SOURCES)):
            if i == BL_Select(2,i):
                print "     %s: " % SOURCES[i] + " ".join(["%5.2fV" % BL_Range(n) for n in range(BL_Count(3)-1,-1,-1)])
        #
        # Set up to capture MY_SIZE samples at MY_RATE from CH-A via the POD input using the highest range.
        #
        BL_Mode(MY_MODE) # prefered capture mode
        BL_Select(BL_SELECT_CHANNEL,MY_CHANNEL); # choose the channel
        BL_Size(100); # optional default BL_MAX_SIZE
        print BL_Rate(BL_MAX_RATE); # optional, default BL_MAX_RATE
        BL_Intro(0.000005); # optional, default BL_ZERO
        BL_Select(BL_SELECT_SOURCE,BL_SOURCE_POD); # use the POD input */
        print BL_Offset(-4.6); # optional, default 0
        print BL_Range(BL_Count(BL_COUNT_RANGE)); # maximum range
        print BL_Trigger(0.1-4.6,BL_TRIG_RISE); # optional when untriggered */
        BL_Enable(TRUE); # at least one channel must be initialised 
        #
        # Perform an (untriggered) trace (this is the actual data capture).
        #
        #
        # Acquire (i.e. upload) the captured data (which may be less than MY_SIZE!).
        n = 200
        amplitudes = np.zeros(n)
        #
        for i in range(n):
            BL_Trace(BL_TRACE_FOREVER)
            data = np.array(BL_Acquire())
            amp = np.max(data) - np.min(data)
            if amp <= 0.: continue
            amplitudes[i] = amp
            print("")
            print(i)
            print(amplitudes[i])
            #plt.plot(data)
            #plt.show()


        bins = np.linspace(0, 10, 101)
        plt.hist(amplitudes, bins=bins, histtype="step")
        plt.show()

        #
        # Close the library to release resources (we're done).
        #
        BL_Close()
        print "Finished: Library closed, resources released."
    else:
        print "  FAILED: device not found (check your probe file)."
    
if __name__ == "__main__":
    import sys
    sys.exit(main())
