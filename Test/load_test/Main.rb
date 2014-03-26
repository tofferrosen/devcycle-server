#!/usr/bin/ruby
require_relative 'framework/load.rb'


class Main

#Different configurations
#specified in config file
#Arrays of Arrays
@configs = Array.new

def self.start(config_file)

    #check if exists
      if not ARGV[0] == nil or not ARGV[0].empty?

        config_file = ARGV[0]
        config_path = "configs/#{config_file}"

        #check if file specified exist
        if not File.exist?(config_path) and not File.file?(config_path)

          puts "ERROR: #{config_file} not a file."

        else

          if not check_format?(config_path)

            puts "Error: #{config_file} incorrect File Format."

          else

            #Create the Load Test here
            test = Load.new(@configs)

            #Start Test
            test.start

          end#conditional branch

        end#file exists

      else
        puts "ERROR: No Config file provided"
      end#nil

  end#Main


  #
  #
  #
  # @param - config file
  # @return - Boolean
  def self.check_format?(file)
    count = 0
    config = Array.new
    File.open(file, "r") do |f|

      f.each_line do |line|

        #ignore comments and empty lines
        if not line.match(/^#/) and not line.strip.empty?
          count+=1
          if line.match(/^-/)
            count = 0

          elsif count == 1 #url
            if not line.is_a?(String) then return false end #check if url
            config.push(line.strip)

          elsif count == 2 #parallel count
            if not line.strip.to_i.is_a?(Integer) then return false end
            config.push(line.strip.to_i)

          elsif count == 3 #json file
            json = line.strip
            json_path = "jsons/#{json}"
            if not File.exist?(json_path) and not File.file?(json_path) then return false end
            config.push(json)
            @configs.push(config) #push configuration
            config = Array.new

            count = 0

          end#conditional branch

        end#if

      end#each_line

    end#file.open

    return true

  end#check_format

end#class


#Call Main
Main.start(ARGV.first)