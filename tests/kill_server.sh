
# =============================================
#
# Kill an MLflow tracking server by port number
# 
# =============================================

if [ $# -lt 1 ] ; then
  echo "$0: Expecting MLflow Tracking Server port"
  exit 1
  fi
port=$1

pids=`lsof -n -i :$port | awk ' { print ( $2 ) } ' | grep -v PID`
echo "PIDs: $pids"
echo "Killing MLflow Tracking Server running on port $port"
for pid in $pids ; do
  echo "Killing PID $pid"
  kill $pid
  done
