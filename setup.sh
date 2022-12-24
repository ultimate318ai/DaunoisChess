noir='\e[0;30m'
gris='\e[1;30m'
rougefonce='\e[0;31m'
rose='\e[1;31m'
vertfonce='\e[0;32m'
vertclair='\e[1;32m'
orange='\e[0;33m'
jaune='\e[1;33m'
bleufonce='\e[0;34m'
bleuclair='\e[1;34m'
violetfonce='\e[0;35m'
violetclair='\e[1;35m'
cyanfonce='\e[0;36m'
cyanclair='\e[1;36m'
grisclair='\e[0;37m'
blanc='\e[1;37m'

neutre='\e[0;m'

liste_packages=("pygame" "chess" "pygame_menu" "sys" "pygame_widgets" "svglib")


echo -e "Welcome to the installation program of Daunoischess.\n Press any key to continue."
read ans

if [ "$(dpkg-query -W -f='${Status}' python3 2>/dev/null | grep -c "ok installed")" -eq 0 ];
then
    echo -e "${rougefonce} Python3 is not installed on your device ⛔️,${neutre} do you want to install it ? [y/n]"
    read ans_python
    if [ "$ans_python" == "y" ]; 
    then
        echo "installing python3...."
        sudo apt-get --force-yes --yes install python3 -qq
    elif [ "$ans_python" == "n" ];
    then 
        echo "python3 is needed for the instalation do be successful sorry..."
        return
    else
        echo "answer not in list : [y, n] : exiting..."
        return
    fi
fi
echo -e "${vertclair} python3 is installed on device ✅${neutre}"
echo -e "Press any key to continue or q to quit."
read ans
echo -e "creating the virtual env... 🌐"
python3 -m venv daunoischess_env
echo -e "Virtual env created ✅"

echo "installing the needed packages for python"
for i in "${liste_packages[@]}"; do
  if [ "$(dpkg-query -W -f='${Status}' "$i" 2>/dev/null | grep -c "ok installed")" -eq 0 ];
    then
        echo -e "${jaune} $i is not installed on your device ⚠️, installing $i... ${neutre}"
        pip install -q "$i"
    fi
    echo -e "$i installed ✅"
done
echo "intallation terminated! 🔝🔝🔝🔝"
echo -e "going into it...🚀"
echo -e "done ✅"
