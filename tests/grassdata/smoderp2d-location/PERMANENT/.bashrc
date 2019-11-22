test -r ~/.alias && . ~/.alias
PS1='GRASS 7.8.0 (smoderp2d-location):\w > '
grass_prompt() {
    MAPSET_PATH="`g.gisenv get=GISDBASE,LOCATION_NAME,MAPSET separator='/'`"
    LOCATION="$MAPSET_PATH"
    if test -f "$MAPSET_PATH/cell/MASK" && test -d "$MAPSET_PATH/grid3/RASTER3D_MASK" ; then
        echo [2D and 3D raster MASKs present]
    elif test -f "$MAPSET_PATH/cell/MASK" ; then
        echo [Raster MASK present]
    elif test -d "$MAPSET_PATH/grid3/RASTER3D_MASK" ; then
        echo [3D raster MASK present]
    fi
}
PROMPT_COMMAND=grass_prompt
export PATH="/usr/lib/grass78/bin:/usr/lib/grass78/scripts:/home/martin/.grass7/addons/bin:/home/martin/.grass7/addons/scripts:/home/martin/Documents:/home/martin/git/gismentors/grass-gis-irsae-winter-course-2018/_static/scripts:/opt/git/gismentors/grass-gis-irsae-winter-course-2018/_static/scripts:/home/martin/Documents:/home/martin/git/gismentors/grass-gis-irsae-winter-course-2018/_static/scripts:/opt/git/gismentors/grass-gis-irsae-winter-course-2018/_static/scripts:/home/martin/Documents:/home/martin/git/gismentors/grass-gis-irsae-winter-course-2018/_static/scripts:/opt/git/gismentors/grass-gis-irsae-winter-course-2018/_static/scripts:/home/martin/.local/bin:/home/martin/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games"
export HOME="/home/martin"
