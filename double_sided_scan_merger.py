# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 09:32:52 2017

@author: Thomas Stehle 
"""

import os
import re
import fnmatch
import PyPDF2
import datetime
import argparse

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

class scan_merger(object):
    """ This class merges two PDF files in a given scan dir. Merging is under the assumption
    that the first (indicated by sorting the file names) file contains all odd pages and the 
    second file contains all even pages in reverse order. This order comes when a scanner with 
    an automatic document feeder (ADF) is used in a two-pass manner: During the first run, all front pages are 
    scanned. In the second run, all back pages are scanned in reverse order as this is the way they come out of 
    the first run.
    This class was extensively tested during development using test-driven development (TDD).
    """
    exception_message_not_same_length = 'PDFs to merge do not have the same length'

    def __init__(self, scan_dir, result_dir):
        """ 
        Constructor.
        
        Args:
            scan_dir: folder location of the source pdfs
            result_dir: folder location of the merged pdf
            
        """
        self.scan_dir = scan_dir
        self.result_dir = result_dir
    
    
    def _get_pdf_files_in_scan_dir(self):
        """ 
        Lists files in the scan dir and returns a list of pdf files contained therein.
        
        Returns:
            List of PDF files in scan_dir
        """
        files_in_dir = os.listdir(self.scan_dir)
        pdf_files_in_dir = [os.path.join(self.scan_dir, afile) for afile in files_in_dir if fnmatch.fnmatch(afile, '*.pdf')]
        return pdf_files_in_dir
    
    
    def _select_pdfs_to_merge(self):
        """
        Gets list of PDFs in scan_dir and sorts them using natural sort. The 
        first two files in the sorted list are returned as PDFs to be merged.
        
        Returns:
            List of length 2 containing PDF files to be merged.
        """
        candidates_to_merge = self._get_pdf_files_in_scan_dir()
        if len(candidates_to_merge) < 2: return list()
        sorted_candidate_list = natural_sort(candidates_to_merge)
        return sorted_candidate_list[0:2]
    
    @staticmethod
    def _pdfs_have_same_length(pdf1, pdf2):
        """ Checks whether two PDF files have the same number of pages.
        
        Returns:
            True: if they have the same number of pages
            False: otherwise
        """
        return pdf1.getNumPages() == pdf2.getNumPages()
    
 
    def _combine_pdfs(self, pdf_in1, pdf_in2, pdf_out):
        """
        Combine two PDFs given the assumption that one contains the odd pages
        and the other one the even pages in reverse order.
        
        Args:
            pdf_in1: PDF containing all odd pages
            pdf_in2: PDF containing all even pages in reverse order
            pdf_out: PDF into which the pages are inserted in the correct order
        """
        num_pages = pdf_in1.getNumPages()
        for page_idx in range(num_pages):
            one_page = pdf_in1.getPage(page_idx)
            other_page = pdf_in2.getPage(num_pages-1 - page_idx)
       
            pdf_out.addPage(one_page)
            pdf_out.addPage(other_page)
        
    
    def merge_pdfs(self):
        """
        Gets the first two PDFs in the scan_dir and merges them into one PDF in
        the correct order. It is assumed that the first PDF contains all odd pages 
        and the second one contains all even pages in reverse order.
        
        Args:
            outfile: filename of result PDF
        """
        pdfs_to_merge = self._select_pdfs_to_merge()
        if len(pdfs_to_merge) == 0: return

        first_pdf = PyPDF2.PdfFileReader(open(pdfs_to_merge[0], 'rb'))
        second_pdf = PyPDF2.PdfFileReader(open(pdfs_to_merge[1], 'rb'))
        if not self._pdfs_have_same_length(first_pdf, second_pdf): 
            raise Exception(self.exception_message_not_same_length)
        
        output_pdf = PyPDF2.PdfFileWriter()
        self._combine_pdfs(first_pdf, second_pdf, output_pdf)
        
        now = datetime.datetime.now()
        outfile = "{}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}.pdf".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
        outfile = os.path.join(self.result_dir, outfile)
        print (outfile)
        
        with open(outfile, 'wb') as fh:
            output_pdf.write(fh)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('src_dir')
    parser.add_argument('dst_dir')
    
    args = parser.parse_args()
    
    merger = scan_merger(args.src_dir, args.dst_dir)
    merger.merge_pdfs()
    