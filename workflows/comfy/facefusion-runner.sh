#! /bin/bash
set -ex

# we're invoked as 
# ./facefusion-runner.sh --input-audio $input_audio --input-video --output $output
LONGOPTS=input_audio:,input_video:,output:
OPTIONS=a:v:o:

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@") || exit 2
# read getopt’s output this way to handle the quoting right:
eval set -- "$PARSED"


while true; do
  case "$1" in
    -a|--input_audio)
      input_audio="$2"
      shift 2
      ;;
    -v|--input_video)
      input_video="$2"
      shift 2
      ;;
    -o|--output)
      output="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Programming error"
      exit 3
      ;;
  esac
done

echo "input_audio: $input_audio"
echo "input_video: $input_video"
echo "output: $output"

export input_audio
export input_video
export output

deactivate || true

cd /facefusion
# Set up the environment
source venv/bin/activate

TEMPDIR=$(mktemp -d)


venv/bin/python3 run.py -s $input_audio -t $input_video --frame-processors lip_syncer --execution-provider cuda -o $TEMPDIR/1.mp4 --headless
venv/bin/python3 run.py -s $input_audio -t $TEMPDIR/1.mp4 --frame-processors face_enhancer --execution-provider cuda -o $output --headless

# rm -rf $TEMPDIR