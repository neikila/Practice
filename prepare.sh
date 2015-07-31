rm -rf standAlone
mkdir standAlone
mkdir standAlone/out
version=${1}
if [ $# -eq 0 ] ; then
  version=0
fi
echo version = $version
cp model.py standAlone/.
cp painter.py standAlone/.
cp input_configs/INPUTv${version}.dat standAlone/INPUT.dat
cp OUTPUT.dat standAlone/.
cp simulation.py standAlone/.
cp startSettings.py standAlone/.
