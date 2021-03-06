# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats, sparse
from collections import Counter
from myms import *

def deconvolute(SpectrumInfo, SpectraLibrary, tol, Top10First, level=1):
    window = SpectrumInfo[1]
    windowMZ = (window[0] + window[1]) / 2.0
    spectrumRT = SpectrumInfo[2]
    index = SpectrumInfo[3]

    DIASpectrum = np.array(SpectrumInfo[0])
    if DIASpectrum.shape[0] == 0:
        return [[0, index, 0, 0, windowMZ, spectrumRT, level, 0]]
    RefSpectraLibrary = SpectraLibrary.copy()

    PrecursorCandidates = list(RefSpectraLibrary.keys())
    if 'PrecursorRT' in list(SpectraLibrary.values())[0]:
        PrecursorCandidates = [key for key,spectrum in RefSpectraLibrary.items()
                                if spectrumRT-5 < float(spectrum['PrecursorRT']) < spectrumRT+5]

    CandidateLibrarySpectra = [RefSpectraLibrary[key]['Spectrum'] for key in PrecursorCandidates]

    peaknum = len(DIASpectrum)
    while True:
        MergedSpectrumCoordIndices = np.searchsorted(DIASpectrum[:, 0] + tol * DIASpectrum[:, 0], DIASpectrum[:, 0])
        MergedSpectrumCoords = DIASpectrum[np.unique(MergedSpectrumCoordIndices), 0]
        MergedSpectrumIntensities = [np.mean(DIASpectrum[np.where(MergedSpectrumCoordIndices == i)[0], 1]) for i in
                                    np.unique(MergedSpectrumCoordIndices)]
        DIASpectrum = np.array((MergedSpectrumCoords, MergedSpectrumIntensities)).transpose()
        if peaknum == len(DIASpectrum):
            break
        peaknum = len(DIASpectrum)

    CriticalMZs = np.concatenate(
        (DIASpectrum[:, 0] - tol * DIASpectrum[:, 0], DIASpectrum[:, 0] + tol * DIASpectrum[:, 0]))
    CriticalMZs = np.sort(CriticalMZs)

    LocateReferenceCoordsInDIA = [np.searchsorted(CriticalMZs, lib[:, 0]) for lib in CandidateLibrarySpectra]

    TopTenPeaksCoordsInDIA = [np.searchsorted(CriticalMZs, M[np.argsort(-M[:, 1])[0:min(10, M.shape[0])], 0]) for M
                              in CandidateLibrarySpectra]

    ReferencePeaksInDIA = [i for i in range(len(PrecursorCandidates)) if
                           len([a for a in TopTenPeaksCoordsInDIA[i] if a % 2 == 1]) > 5
                           ]

    IdentPrecursorsLocations = [LocateReferenceCoordsInDIA[i] for i in ReferencePeaksInDIA]

    IdentPrecursorSpectra = [CandidateLibrarySpectra[i] for i in ReferencePeaksInDIA]

    IdentPrecursors = [PrecursorCandidates[i] for i in ReferencePeaksInDIA]
    if len(IdentPrecursors) == 0:
        return [[0, index, 0, 0, windowMZ, spectrumRT, level, 0]]

    Penalties = np.array([
        np.sum([
            IdentPrecursorSpectra[j][k][1]
            for k in range(len(IdentPrecursorSpectra[j]))
            if IdentPrecursorsLocations[j][k] % 2 == 0
        ]) for j in range(len(IdentPrecursorSpectra))
    ])

    RowIndices = (np.array([i for v in IdentPrecursorsLocations
                                         for i in v if i % 2 == 1])
                               + 1) / 2
    RowIndices = RowIndices - 1
    RowIndices = RowIndices.astype(int)

    ColumnIndices = np.array([
        i for j in range(len(IdentPrecursors))
        for i in [j] * len([k for k in IdentPrecursorsLocations[j] if k % 2 == 1])
    ])

    MatrixIntensities = np.array([
        IdentPrecursorSpectra[k][i][1]
        for k in range(len(IdentPrecursorSpectra))
        for i in range(len(IdentPrecursorSpectra[k]))
        if IdentPrecursorsLocations[k][i] % 2 == 1
    ])

    UniqueRowIndices = list(set(RowIndices))
    UniqueRowIndices.sort()
    DIASpectrumIntensities = DIASpectrum[UniqueRowIndices, 1]

    relatedLibNums = Counter(RowIndices)
    counter_keys = np.array(list(relatedLibNums.keys()))
    counter_values = np.array(list(relatedLibNums.values()))

    unique_mz_ids = counter_keys[np.where(counter_values == 1)]
    unique_mz_lib_ids = np.array(
        [ColumnIndices[np.where(RowIndices == mz_id)] for mz_id in unique_mz_ids])
    unique_mz_lib_ids = unique_mz_lib_ids.reshape(1, -1)[0]

    flag = False
    output = []
    for i in range(len(IdentPrecursors)):
        coeff = 0
        unique_mz_ids_of_thislib = unique_mz_ids[np.where(unique_mz_lib_ids == i)]
        if len(unique_mz_ids_of_thislib) > 0:
            FeaturedPeakIntensitiesInDIA = DIASpectrum[unique_mz_ids_of_thislib, 1]
            FeaturedPeakIntensitiesInLib = np.array(
                [MatrixIntensities[np.where(RowIndices == mz_id)] for mz_id in unique_mz_ids_of_thislib])
            FeaturedPeakIntensitiesInLib = FeaturedPeakIntensitiesInLib.reshape(1, -1)[0]

            if Top10First:
                CandidateIndex = np.where(FeaturedPeakIntensitiesInLib >= MinIntensityDic[IdentPrecursors[i]])
                if len(CandidateIndex[0]) > 0:
                    FeaturedPeakIntensitiesInDIA = FeaturedPeakIntensitiesInDIA[CandidateIndex]
                    FeaturedPeakIntensitiesInLib = FeaturedPeakIntensitiesInLib[CandidateIndex]

            coeff = cal_nnls(list(FeaturedPeakIntensitiesInLib), list(FeaturedPeakIntensitiesInDIA), Penalties[i])
        else:
            flag = True
        output.append(
            [coeff, index, IdentPrecursors[i][0], IdentPrecursors[i][1], windowMZ, spectrumRT, level])

    RowIndices = stats.rankdata(RowIndices, method='dense').astype(int) - 1
    if flag and level < 50:
        LibraryMatrix = sparse.coo_matrix((MatrixIntensities, (RowIndices, ColumnIndices)))
        LibraryCoeffs = [i[0] for i in output]
        FittingIntensities = LibraryMatrix * LibraryCoeffs
        FittingIntensities = FittingIntensities.reshape(1, -1)[0]
        DIASpectrum[UniqueRowIndices, 1] = DIASpectrum[UniqueRowIndices, 1] - FittingIntensities

        DIASpectrum[:, 1][np.where(DIASpectrum[:, 1] < 0)] = 0

        output = [out for out in output if out[0] > 0]
        CopyLibrary = SpectraLibrary.copy()
        for out in output:
            CopyLibrary.pop((out[2], out[3]))
        SpectrumInfo[0] = DIASpectrum
        output.extend(deconvolute(SpectrumInfo, CopyLibrary, tol, Top10First, level + 1))

    if level == 1:
        LibraryMatrix = sparse.coo_matrix((MatrixIntensities, (RowIndices, ColumnIndices)))
        LibraryCoeffs = []
        for lib_id in range(len(IdentPrecursors)):
            for out in output:
                if (IdentPrecursors[lib_id] == (out[2], out[3])):
                    LibraryCoeffs.append(out[0])
        FittingIntensities = LibraryMatrix * LibraryCoeffs
        FittingIntensities = FittingIntensities.reshape(1, -1)[0]

        Correlation = pd.DataFrame([FittingIntensities, DIASpectrumIntensities]).T.corr()[0][1]
        for i in output:
            i.append(Correlation)

    return output


def run(mzmlnames, libnames, ppm=20, distance=100.0, fdr=0.01, dec_type="", fea_ions="Default", ms_data_type="DIA"):
    #args = sys.argv
    # mzml = "E:/Workspace/Download/protein_data/mzml/CS20170831_SV_HEK_SpikeP100_27ng_Overlap22_01"
    # libname = "E:/Workspace/Download/protein_data/lib/HEKAndP100HeavyLib"
    libname = str(libnames[0]).split('.blib')[0]

    tol = int(ppm)
    Top10First = False
    if fea_ions != "Default":
        Top10First = True
    # print('Top10First', Top10First)
    with open('log.txt', 'a') as f:
        print('Top10First', Top10First, file=f)
    distance = distance

    # print('Loading library...')
    with open('log.txt', 'a') as f:
        print('Loading library...', '---', os.path.basename(mzmlnames[0]), file=f)
    SpectraLibrary = LoadBlib(os.path.expanduser(libname+'.blib'))
    SpectraLibrary = LibraryNormalization(SpectraLibrary)
    # print('Finished')

    # print('Generating decoy library...')
    with open('log.txt', 'a') as f:
        print('Generating decoy library...', '---', os.path.basename(mzmlnames[0]), file=f)
    DecoyLibrary = GenerateDecoyLibrary(SpectraLibrary, distance)
    # print('Finished')

    if Top10First:
        TargetDecoyLibrary = DecoyLibrary.copy()
        TargetDecoyLibrary.update(SpectraLibrary)
        global MinIntensityDic
        MinIntensityDic = {k : np.sort(v['Spectrum'][:,1])[-min(10,len(v['Spectrum']))] for k,v in TargetDecoyLibrary.items()}

    
    mzml = str(mzmlnames[0]).split('.mzML')[0]
    # print('Loading MS2...')
    with open('log.txt', 'a') as f:
        print('Loading MS2...', '---', os.path.basename(mzmlnames[0]), file=f)
    MS2 = LoadMS2(mzml + '.mzML')
    # print('Finished')

    windows = set(np.array(MS2)[:, 1])
    DividedLibraries = DivideLibraryByWindows(SpectraLibrary, windows)
    DividedDecoyLibraries = DivideLibraryByWindows(DecoyLibrary, windows)

    header = [[(x[1][0] + x[1][1]) / 2, x[2], x[3]] for x in MS2]
    header = pd.DataFrame(header)
    dirPath = mzml
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    header.to_csv(os.path.join(dirPath, 'header.csv'), index=False, header=False)
    # print("Header has written.")
    with open('log.txt', 'a') as f:
        print('Header has written.', '---', os.path.basename(mzmlnames[0]), file=f)

    output = []
    ms2_num = MS2[-1][3]
    for spectrum in MS2:
        if spectrum[3] % 1000 == 0:
            with open('log.txt', 'a') as f:
                print('Deconvoluting ' + str(spectrum[3]) + '...' + str(ms2_num), '---', os.path.basename(mzmlnames[0]), file=f)
        output.extend(deconvolute(spectrum, DividedLibraries[spectrum[1]], tol * 1e-6, Top10First))
    # print('Finished')

    dirPath = os.path.join(dirPath, os.path.basename(libname) + '_' + str(tol) + 'ppm')
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    targetCoeffs = pd.DataFrame(output)
    targetCoeffs.to_csv(os.path.join(dirPath, 'Coeffs.csv'), index=False, header=False)
    #print("Coeffs have written.")
    with open('log.txt', 'a') as f:
        print('Coeffs have written.', '---', os.path.basename(mzmlnames[0]), file=f)

    output_decoy = []
    for spectrum in MS2:
        if spectrum[3] % 1000 == 0:
            with open('log.txt', 'a') as f:
                print('Re-deconvoluting ' + str(spectrum[3]) + '...' + str(ms2_num), '---', os.path.basename(mzmlnames[0]), file=f)
        output_decoy.extend(deconvolute(spectrum, DividedDecoyLibraries[spectrum[1]], tol * 1e-6, Top10First))
    # print('Finished')

    decoyCoeffs = pd.DataFrame(output_decoy)
    decoyCoeffs.to_csv(os.path.join(dirPath, 'DecoyCoeffs.csv'), index=False, header=False)
    #print("Decoy coeffs have written.")
    with open('log.txt', 'a') as f:
        print('Decoy coeffs have written.', '---', os.path.basename(mzmlnames[0]), file=f)
        print('Start Quant..............', '---', os.path.basename(mzmlnames[0]), file=f)
