from __future__ import annotations
import math
from dbetto import TextDB
import os
from typing import Any


def ask_and_print_runs(node: Any) -> None:
    ans = input("Do you want to see the full list of available runs, runXXXX: [phi, x, z] ? [y/N]: ").strip().lower()
    if ans in ("y", "yes"):
        for run in node.keys():
            print(f"{run}:  {list(getattr(node, run).source_position.values())}")


def check_source_position(
    node: Any,
    user_positions: list[float],
    hpge_name: str,
    campaign: str,
    measurement: str
) -> None:
    
    phi_position, r_position, z_position = user_positions[0], user_positions[1], user_positions[2]
    phi_pos= list(node.group("source_position.phi_in_deg").keys())
    if phi_position not in phi_pos:
        print(f"Position ERROR: Provided phi position {phi_position} not found in the database for the given measurement {hpge_name}/{campaign}/{measurement}.\n" 
        "Available phi positions are: " + str(phi_pos))
        ans = input("Do you want to see the full list of available runs, runXXXX: [phi, x, z] ? [y/N]: ").strip().lower()
        if ans in ("y", "yes"):
            for run in node.keys():
                print(f"{run}:  {list(getattr(node, run).source_position.values())}")
        raise ValueError(f"Provided phi position {phi_position} not found in the database for the given measurement {hpge_name}/{campaign}/{measurement}.")
    else:
        data = node.group("source_position.phi_in_deg").get(phi_position)
        r_available=[]
        z_available=[]
        matched_r = []
        for i in data.keys():
            matched_z = False
            try:
                r_pos_=data.get(i).get('source_position').get('r_in_mm')
            except AttributeError:
                r_pos_ = data.get('source_position').get('r_in_mm')
            if r_position!=r_pos_:
                matched_r.append(False)
                if r_pos_ not in r_available:
                    r_available.append(r_pos_)
                continue
            else:
                matched_r.append(True)
                try:
                    z_pos_=data.get(i).get('source_position').get('z_in_mm')
                except:
                    z_pos_ = data.get('source_position').get('z_in_mm')
                if z_position!=z_pos_:
                    matched_z = False
                    if z_pos_ not in z_available:
                        z_available.append(z_pos_)
                    continue
                else: 
                    matched_z = True
                    try:
                        run = data.get(i).get('run')
                    except:
                        run = data.get('run')
                    return run
        if not any(matched_r):
            print(f"Position ERROR: Provided r position {r_position} not found in the database for the given measurement {hpge_name}/{campaign}/{measurement}.\n" 
            "For the provided phi position " + str(phi_position) +"\n"
            "the available r positions are: " + str(r_available))
            ask_and_print_runs(node)
            raise ValueError(f"Provided r position {r_position} not found in the database for the given measurement  {hpge_name}/{campaign}/{measurement}.")
        if matched_z==False:
            print(f"Position ERROR: Provided z position {z_position} not found in the database for the given measurement  {hpge_name}/{campaign}/{measurement}.\n" 
            "For the provided phi position " + str(phi_position) +" and r position " + str(r_position) +"\n"
            "the available z positions are: " + str(z_available))
            ask_and_print_runs(node)
            raise ValueError(f"Provided z position {z_position} not found in the database for the given measurement  {hpge_name}/{campaign}/{measurement}.")


def set_source_position(config: dict) -> tuple[str, list, list]:

    hpge_name   = config.hpge_name
    campaign    = config.campaign
    measurement = config.measurement
    run         = config.run
    phi_position= config.phi_position
    r_position  = config.r_position
    z_position  = config.z_position

    MetaDataPath="/global/cfs/cdirs/m2676/data/teststands/hades/prodenv/ref/v1.0.0/inputs/hardware/config"
    MeasurementPath=f"{MetaDataPath}/{hpge_name}/{campaign}/{measurement}.yaml"
    if not os.path.isfile(MeasurementPath):
        raise FileNotFoundError(f"The measurement {MeasurementPath} does not exist. Please check the configuration file and metadata.")


    source_type = measurement[:6]
    position    = measurement[7:10]


    db = TextDB(MetaDataPath)
    node = getattr(db, hpge_name)
    node = getattr(node, campaign)
    node = getattr(node, measurement)

    if run.isdigit(): #the user knows the run number
        run="run"+run
        try:
            node = getattr(node, run)
        except AttributeError:
            raise ValueError(f"Run '{run}' not found in the metadata. Run names must be 4-digit strings with leading zeros, e.g., '0001'.")
                                
        phi_position = node.source_position.phi_in_deg
        r_position = node.source_position.r_in_mm
        z_position = node.source_position.z_in_mm
        run=run[:1]+run[4:]  
    else: #the user knows the source position
        user_positions = [phi_position, r_position, z_position]

        run=check_source_position(node, user_positions, hpge_name, campaign, measurement)
        run=run[:1]+run[4:]

    if source_type=="am_HS1" and r_position!=0: #update this condition
        r_position +=-66
        if r_position<0:
            phi_position+=180
            r_position=abs(r_position)
    phi=phi_position*math.pi/180.
    x_position=round(r_position*math.cos(phi),2)
    y_position=round(-r_position*math.sin(phi),2)

    #position in gdml file
    DefinePositions=[x_position,y_position,z_position]

    if position=="top":
        z_position=-z_position
    #position of radioactive source in .mac file    
    ListPosition=[x_position,y_position,z_position]
    if source_type=='ba_HS4' :
        pass
    #check numbers below
    elif source_type=='th_HS2' :
        if position=='top':
            ListPosition[2]+= -5.     #(3.+.5+1.5)mm
        elif position=='lat':
            if ListPosition[1]==0:
                ListPosition[1]=82.3 #(60.8.+18.+3.+.5)mm
            else:
                ListPosition[1]+= 21.5    #(18.+3.+.5)mm
    elif source_type=='am_HS1':
        ListPosition[2]+= -26.8   #(25.6+0.2+1.) mm
    #else: #am_HS6
        #ListPosition[2]+= 1   #(25.6+0.2+1.) mm
    return  run, DefinePositions, ListPosition

