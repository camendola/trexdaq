#include <stdio.h>
#include <limits.h>
#include <bitlib.h>
#include <stdio.h>


#define MY_DEVICES 1 /* open one device only */
#define MY_PROBE_FILE "" /* default probe file if unspecified */

#define MY_DEVICE 0
#define MY_CHANNEL 0
#define MY_TRIGGER_CHANNEL 0
#define MY_MODE BL_MODE_DUAL
#define MY_RATE 1000000 /* capture sample rate */
#define MY_SIZE 100 /* number of samples to capture */


int main(int argc, char *argv[]) {
   const int n = MY_SIZE;
   /* 
    * Open and select the first channel on the first device.
    */
    printf("\nStarting: Attempting to open %d device%s...\n",MY_DEVICES,MY_DEVICES!=1?"s":"");
    if ( ! BL_Open(MY_PROBE_FILE,MY_DEVICE) ) {
        printf("Failed to find a devices.\n");
        BL_Close(); /* call this to release library resources */
	return 1;
    }
    if ( BL_Select(BL_SELECT_DEVICE,MY_DEVICE) != MY_DEVICE ) {
        printf("Failed to select device %d.\n",MY_DEVICE);
        BL_Close(); /* call this to release library resources */
	return 1;
    }
    if ( BL_Select(BL_SELECT_CHANNEL,MY_CHANNEL) != MY_CHANNEL ) {
        printf("Failed to select channel %d.\n",MY_CHANNEL);
    	BL_Close(); /* call this to release library resources */
	return 1;
    }   
   /* 
    * Prepare to capture one channel...
    */
    if ( BL_Mode(MY_MODE) != MY_MODE ) {
        printf("Failed to select mode %d.\n",MY_MODE);
	return 1;
    }
 
    // For the trigger channel
    //BL_Select(BL_SELECT_CHANNEL,MY_TRIGGER_CHANNEL); // Select trigger channel
    //BL_Trigger(1.0,BL_TRIG_RISE); // optional when untriggered

    /* For the pulse channel */
    BL_Select(BL_SELECT_CHANNEL,MY_CHANNEL);
    BL_Size(MY_SIZE);
    BL_Select(BL_SELECT_SOURCE,BL_SOURCE_POD);
    BL_Offset(-4.6);
    BL_Range(BL_Count(BL_COUNT_RANGE));
    BL_Trigger(-4.5,BL_TRIG_RISE);
    BL_Enable(true);
   /* 
    * Capture and acquire the data...
    */
    printf("   Trace: %d samples @ %.0fHz = %fs\n",BL_Size(BL_ASK),BL_Rate(BL_ASK), BL_Time(BL_ASK));
    double data[n];
    //int j = 0;
    while(true) {
        if ( BL_Trace(BL_TRACE_FOREVER,BL_SYNCHRONOUS) ) { /* capture data (without a trigger) */
            int i;
            BL_Select(BL_SELECT_CHANNEL,MY_CHANNEL); /* optional if only one channel */
            if ( BL_Acquire(n, data)  == n ) { /* acquire (i.e. dump) the capture data */
		//if(j % 100 == 0) {
                //    printf(" %d", j);
                //    printf("\n");
		//}
		//++j;
                //printf("Acquired:");
                for (i = 0; i < n; i++)
                    printf(" %f", data[i]);
                printf("\n");
            }
	}
    }
    //printf("Data acquisition complete. Dump Log...\n");
    //printf("%s\n",BL_Log());

    BL_Close(); /* call this to release library resources */
}
