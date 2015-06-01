import MySQLdb as mdb
from difflib import SequenceMatcher as SM
import re

def fuzzy_match(orig, comp):
    seq = SM(None, orig, comp)
    score = seq.ratio() * 100
    return score

def compare_1point(row, comp):
    score = 0
    r_type = row[1]
    r_name = row[2]
    r_dob = row[3]
    r_isop = row[4]
    r_gender = row[5]
    r_spec = row[6]
    r_spec2 = row[7]
    
    c_type = comp[1]
    c_name = comp[2]
    c_dob = comp[3]
    c_isop = comp[4]
    c_gender = comp[5]
    c_spec = comp[6]
    c_spec2 = comp[7]

    threshold = 70
    if (r_gender != None and c_gender != None) and fuzzy_match(r_gender, c_gender) >= threshold:
    		score += 1
    if (r_spec != None and c_spec != None) and fuzzy_match(r_spec, c_spec) >= threshold:
    		score += 1
    if (r_spec2 != None and c_spec2 != None) and fuzzy_match(r_spec2, c_spec2) >= threshold:
    		score += 1
   
    return score
    
    
def checkAddress(r_street,r_city, r_country, r_county, r_postcode, r_unit, r_region, c_street, c_city, c_county, c_country, c_postcode, c_unit, c_region):
    score = 0
    
    if r_street != None and c_street != None and r_street == c_street:
      	score += 3
    
    if r_city != None and c_city != None and r_city == c_city:
    	score += 1
        
    if r_country != None and c_country != None and r_country == c_country:
    	score += 1
        
    if r_county != None and c_county != None and r_county == c_county:
    	score += 1
        
    if r_postcode != None and c_postcode != None and r_postcode == c_postcode:
    	score += 1
        
    if r_unit != None and c_unit != None and r_unit == c_unit:
    	score += 1
        
    if r_region != None and c_region != None and r_region == c_region:
    	score += 1
    
    return score
  
def compare(row, comp):
    score = 0

    r_type = row[1]
    r_name = row[2]
    r_dob = row[3]
    r_isop = row[4]
    r_gender = row[5]
    r_spec = row[6]
    r_spec2 = row[7]
    r_phone = row[8]
    
    c_type = comp[1]
    c_name = comp[2]
    c_dob = comp[3]
    c_isop = comp[4]
    c_gender = comp[5]
    c_spec = comp[6]
    c_spec2 = comp[7]
    c_phone = comp[8]

    if r_type != None and c_type != None and r_type != c_type:
        return False, -1
    
    if c_name != None and r_name != None:
    	if SM(None, c_name.lower(), r_name.lower()).ratio() == 1:
    		score += 6
    	elif SM(None, c_name.lower(), r_name.lower()).ratio() >= .8:
            score += 5
        elif SM(None, c_name.lower(), r_name.lower()).ratio() <= .5:
            score += -6
            return False, -1
    
    if r_isop != None and c_isop != None:
    	if  r_isop == c_isop:
    		score += 1
        else:
        	score += -1
      
    if r_gender != None and c_gender != None:
    	if r_gender == c_gender:
    		score += 1
        else:
        	score += -1
      
    if r_spec != None and c_spec != None:
    	if r_spec == c_spec:
    		score += 1
      	else:
        	score += -1
            
    if r_spec2 != None and c_spec2 != None:
    	if r_spec2 == c_spec2:
    		score += 1
      	else:
        	score += -1
            
    if r_phone != None and c_phone != None:
    	c_phoneClean = re.sub("[^0-9]", "", c_phone)
    	r_phoneClean = re.sub("[^0-9]", "", r_phone)
        
        
    	if r_phoneClean == c_phoneClean:
    		score += 3
      	else:
        	"""
        	score += -1
            """
      
    score += checkAddress(row[9], row[10], row[11], row[12], row[13], row[14], row[15], comp[9], comp[10], comp[11], comp[12], comp[13], comp[14], comp[15])
    score += checkAddress(row[16], row[17], row[18], row[19], row[20], row[21], row[22], comp[16], comp[17], comp[18], comp[19], comp[20], comp[21], comp[22])
    
    
    if score > 8:
    	return True, score
    else:
    	return False, score
      
def match():
    con = mdb.connect(host='csc-db0.csc.calpoly.edu',user='jwilso43',passwd='abc123',db='jwilso43')

    with con:

        cur = con.cursor()

        cur.execute('''SELECT SP.*, PN.PhoneNumber,
                       A1.Street, A1.City, A1.Country, A1.County, A1.PostCode, A1.Unit, A1.Region, 
                       A2.Street, A2.City, A2.Country, A2.County, A2.PostCode, A2.Unit, A2.Region
                       FROM SourceProviders as SP, PhoneNumbers as PN, Addresses as A1, Addresses as A2 
                       WHERE SP.ID = PN.SourceID AND A1.SourceID = SP.ID AND A2.SourceID = SP.ID AND A1.Type = 'm' AND A2.type = 'p'
                    ''')
        rows = cur.fetchall()

        tmp = []
        master = []
        match = {}
        match_id = 0

        TOTAL = 1000

        for i in range(0, TOTAL):
            tmp.append(rows[i])

        print len(tmp)

        count = 0
        match_count = 0
        i = 0
        while i < len(tmp):
            row = tmp[i]
            row_id = row[0]

            if row_id not in match:
               master.append([row])
               match[row_id] = match_id
               match_id += 1

            j = i + 1
            if i % 100 == 0:
                print i

            while j < len(tmp):
                count += 5
                comp = tmp[j]
                comp_id = comp[0]

                result, score = compare(row,comp)
                if result:
                    match_count += 1

                    if comp_id in match:
                        index = match[comp_id]
                        copy = master[index]
                        master[index] = []
                        index = match[row_id]
                        master[index] += copy
                    else:
                        index = match[row_id]
                        match[comp_id] = index
                        print index
                        master[index].append(comp)

                    print '----- MATCH ' + str(score) + ' -----'
                    print row
                    print comp


                j += 1
            i += 1


        print 'comparisons: ' + str(count)
        print 'matches: ' + str(match_count)

        for i in range(0,len(master)):
            r = master[i]
            r_len = len(r)
            if r_len > 1:
               for j in range(0, r_len):
                  print 'source id: ' + str(r[j][0]) 
                  print 'name: ' + r[j][2]
               print '----------'


    con.close()

if __name__ == '__main__':
    match()