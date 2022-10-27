# QUIC Cardinality Estimator Tool Using HyperLogLog Algorithm


This tool is based on the work of Yousra Chabchoub, Georges Hebrail in their
article "Sliding HyperLogLog: Estimating Cardinality in a Data Stream over a
Sliding Window" (2010).

***

## Flags and Setup

```commandline
--help - Get a list of all flags.
```
```commandline
-m <n> or --memory <n> - Set the amount of memory buckets (LFPMs) in memory to n.
                         This number should be a power of 2 and higher or equal to 16.
                         Defaults to 64.
```
```commandline
-v or --verify - Print the actual cardinality to verify error rate.
```
```commandline
-f <path> or --file <path> - Capture from a .pcap (.pcapng) file instead of a live capture.
```
```commandline
-l <path> or --log <path> - Path to log file in which you would like to save your output.
                           Defaults to "<current_folder>\logs\log.txt".
```
```commandline
--src - Enable Small Range Correction with Linear Counting.
        For more information regarding Small Range Correction,
            please refer to the HyperLogLog article (2007).
```

***

## Usage

To run the estimator, run the [Cardinality Estimator](CardinalityEstimator.py) script with the relevant flags.
While the script is running you may enter a number of different inputs as commands.

* *exit* or *quit* - Exit the estimator
* *\<blank input\>* or *estimate* or *cardinality* - Output the cardinality since the estimator started
* *status* - Output the LFPMs contents
* *\<n\>* - Output the cardinality in the last n seconds

Your actions will be automatically logged in the log file set by the **-l** flag (or in the default log file).

**Important Note:** There is currently a problem with logging.

If you are reading from a file, please wait for the file to finish reading before exiting the estimator
(you will be notified when the file reading was finished by the estimator).

If you are using Live Capture, your actions will not be logged.

***

## References

1. [Sliding HyperLogLog: Estimating Cardinality in a Data Stream over a Sliding Window](https://ieeexplore.ieee.org/document/5693443)
by Yousra Chabchoub, Georges Hebrail; 2010.
2. [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
by Philippe Flajolet, Éric Fusy, Olivier Gandouet, Frédéric Meunier; 2007.

***

## Examples

### Running with 64 LFPMs, live capture
Run the command:
```commandline
python CardinalityEstimator.py -m 64
```
After manually running 200 QUIC connections, a blank input outputs:
```commandline
Waiting for input...

Cardinality estimation is: 209
```
After manually running 100 more QUIC connections, a blank input outputs:
```commandline
Waiting for input...

Cardinality estimation is: 284
```
Running `50` (estimating cardinality for the last 50 seconds) outputs:
```commandline
Waiting for input...
50
Current time is: 2022-10-27 12:40:35
        and the cardinality estimation for duration 50.0 is: 139
```
And running `status` outputs:
```commandline
Waiting for input...
status
0: 2 packets:(3, 1666898441.981916000)(0, 1666898482.753045000)
1: 1 packets:(3, 1666898430.515285000)
2: 3 packets:(4, 1666898273.673436000)(2, 1666898422.669759000)(1, 1666898487.949976000)
3: 3 packets:(3, 1666898239.312564000)(1, 1666898393.950083000)(0, 1666898488.150866000)
.
.
.
```

### Running with 256 LFPMs, capturing from file 1000 QUIC connections and with verification
The file is a Wireshark capture of [1000 QUIC connections](./1000%20QUIC%20Connections.pcapng) and is available in the project repository.

Run the command:
```commandline
python CardinalityEstimator.py -m 256 -v -f "./1000 QUIC connections.pcapng"
```
Inserting a blank input while the estimator reads the file outputs:
```commandline
Waiting for input...

Cardinality estimation is: 738
Actual cardinality is: 750
```
After waiting for the estimator to finish reading the file, a blank input outputs:
```commandline
Completed file reading
Waiting for input...

Cardinality estimation is: 1001
Actual cardinality is: 1000
```

### Running with 32 LFPMs, live capture and with verification
Run the command:
```commandline
python CardinalityEstimator.py -m 32 -v
```
While manually running 200 QUIC connections, a blank input outputs:
```commandline
Waiting for input...

Cardinality estimation is: 128
Actual cardinality is: 136
```
After waiting for the 200 connections to finish, a blank input outputs:
```commandline
Waiting for input...

Cardinality estimation is: 185
Actual cardinality is: 200
```
And Running `50` (estimating cardinality for the last 50 seconds) outputs:
```commandline
Waiting for input...
50
Current time is: 2022-10-27 12:59:02
        and the cardinality estimation for duration 50.0 seconds is: 90
        Actual cardinality is: 94
```